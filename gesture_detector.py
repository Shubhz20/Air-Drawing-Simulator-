"""
gesture_detector.py - Gesture recognition engine
==================================================
Translates raw finger states from HandTracker into application gestures.

Two detection strategies are provided:

1. **Rule-based** (default) — fast, deterministic, zero training needed.
   Maps finger-up patterns directly to gestures via a lookup table.

2. **ML-based** (optional) — a lightweight scikit-learn classifier trained
   on collected hand-landmark features.  Enable it by calling
   `train_classifier()` with labelled data, then `use_ml(True)`.

Supported gestures
------------------
  DRAW        Index finger only → draw on canvas
  ERASE       Open palm (all 5 fingers) → eraser mode
  MOVE        Pinch (thumb + index close) → drag canvas
  SELECT      Thumb + pinky up → cycle colour
  UNDO        Thumb + middle up → undo last stroke
  REDO        Thumb + ring up → redo
  SHAPE_RECT  Index + middle up, others down → rectangle tool
  SHAPE_CIRCLE Index + middle + ring up, others down → circle tool
  CLEAR       Fist held for 1.5 s → clear canvas
  IDLE        Anything else → pause drawing
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional

import numpy as np

from config import PINCH_THRESHOLD


# ── Gesture enum ────────────────────────────────

class Gesture(Enum):
    IDLE         = auto()
    DRAW         = auto()
    ERASE        = auto()
    MOVE         = auto()
    SELECT       = auto()
    UNDO         = auto()
    REDO         = auto()
    SHAPE_RECT   = auto()
    SHAPE_CIRCLE = auto()
    CLEAR        = auto()
    SAVE         = auto()


# ── Gesture detector ────────────────────────────

@dataclass
class GestureDetector:
    """
    Converts finger-up patterns and pinch distance into a Gesture.

    Parameters
    ----------
    pinch_threshold : float
        Max normalised distance to count as a pinch.
    fist_hold_secs : float
        Seconds the fist must be held to trigger CLEAR.
    """

    pinch_threshold: float = PINCH_THRESHOLD
    fist_hold_secs: float = 1.5

    # internal state
    _fist_start: Optional[float] = field(default=None, init=False, repr=False)
    _prev_gesture: Gesture = field(default=Gesture.IDLE, init=False, repr=False)
    _use_ml: bool = field(default=False, init=False, repr=False)
    _classifier: object = field(default=None, init=False, repr=False)

    # ── rule-based detection ────────────────────

    def detect(
        self,
        fingers: list[bool],
        pinch_dist: float,
        landmarks=None,
    ) -> Gesture:
        """
        Main entry point.  Call once per frame.

        Parameters
        ----------
        fingers : list of 5 bools  [thumb, index, middle, ring, pinky]
        pinch_dist : float, normalised thumb-index distance
        landmarks : optional MediaPipe hand landmarks (for ML mode)

        Returns
        -------
        Gesture enum value
        """
        # If ML classifier is active and trained, use it
        if self._use_ml and self._classifier is not None and landmarks is not None:
            return self._detect_ml(landmarks)

        return self._detect_rules(fingers, pinch_dist)

    def _detect_rules(self, fingers: list[bool], pinch_dist: float) -> Gesture:
        thumb, index, middle, ring, pinky = fingers

        # ── Pinch (thumb + index close together) → MOVE ──
        if pinch_dist < self.pinch_threshold:
            self._reset_fist()
            return Gesture.MOVE

        # ── Fist (all fingers down) held → CLEAR ──
        if not any(fingers):
            return self._check_fist_hold()

        self._reset_fist()

        # ── Single index finger → DRAW ──
        if fingers == [False, True, False, False, False]:
            return Gesture.DRAW

        # ── All five up (open palm) → ERASE ──
        if all(fingers):
            return Gesture.ERASE

        # ── Index + middle only → SHAPE_RECT (peace / V sign) ──
        if fingers == [False, True, True, False, False]:
            return Gesture.SHAPE_RECT

        # ── Index + middle + ring → SHAPE_CIRCLE ──
        if fingers == [False, True, True, True, False]:
            return Gesture.SHAPE_CIRCLE

        # ── Thumb + pinky ("hang loose") → SELECT (cycle colour) ──
        if fingers == [True, False, False, False, True]:
            return Gesture.SELECT

        # ── Thumb + middle → UNDO ──
        if fingers == [True, False, True, False, False]:
            return Gesture.UNDO

        # ── Thumb + ring → REDO ──
        if fingers == [True, False, False, True, False]:
            return Gesture.REDO

        # ── Thumb + index + pinky ("rock on") → SAVE ──
        if fingers == [True, True, False, False, True]:
            return Gesture.SAVE

        # ── Everything else → IDLE ──
        return Gesture.IDLE

    # ── fist-hold logic ─────────────────────────

    def _check_fist_hold(self) -> Gesture:
        now = time.time()
        if self._fist_start is None:
            self._fist_start = now
        elapsed = now - self._fist_start
        if elapsed >= self.fist_hold_secs:
            self._fist_start = None
            return Gesture.CLEAR
        return Gesture.IDLE   # still waiting

    def _reset_fist(self):
        self._fist_start = None

    # ── ML-based detection (optional) ───────────

    def use_ml(self, enabled: bool):
        """Switch between rule-based and ML-based detection."""
        self._use_ml = enabled

    def train_classifier(self, features: np.ndarray, labels: np.ndarray):
        """
        Train a simple Random Forest classifier on hand-landmark features.

        Parameters
        ----------
        features : ndarray of shape (n_samples, 42)
            Flattened (x, y) of 21 landmarks, normalised to wrist origin.
        labels : ndarray of shape (n_samples,)
            Integer gesture labels matching Gesture enum values.

        Requires scikit-learn (optional dependency).
        """
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import cross_val_score
        except ImportError:
            print("[GestureDetector] scikit-learn not installed. "
                  "Run: pip install scikit-learn")
            return

        clf = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
        )
        scores = cross_val_score(clf, features, labels, cv=5)
        print(f"[GestureDetector] CV accuracy: {scores.mean():.2%} "
              f"(+/- {scores.std():.2%})")

        clf.fit(features, labels)
        self._classifier = clf
        print("[GestureDetector] ML classifier trained and ready.")

    def _detect_ml(self, landmarks) -> Gesture:
        """Run the trained ML classifier on current landmarks."""
        features = self._landmarks_to_features(landmarks)
        pred = self._classifier.predict([features])[0]
        try:
            return Gesture(pred)
        except ValueError:
            return Gesture.IDLE

    @staticmethod
    def _landmarks_to_features(landmarks) -> np.ndarray:
        """
        Convert MediaPipe landmarks to a flat feature vector.
        Normalises all positions relative to the wrist (landmark 0)
        so the gesture is translation-invariant.
        """
        lm = landmarks.landmark
        wrist_x, wrist_y = lm[0].x, lm[0].y
        features = []
        for point in lm:
            features.append(point.x - wrist_x)
            features.append(point.y - wrist_y)
        return np.array(features, dtype=np.float32)

    # ── data collection helper ──────────────────

    @staticmethod
    def collect_training_sample(landmarks) -> np.ndarray:
        """
        Call this while collecting labelled data for ML training.
        Returns the feature vector for the current hand pose.
        """
        return GestureDetector._landmarks_to_features(landmarks)


# ── Human-friendly gesture descriptions ─────────

GESTURE_DESCRIPTIONS = {
    Gesture.IDLE:         "Idle — paused",
    Gesture.DRAW:         "Draw — index finger",
    Gesture.ERASE:        "Erase — open palm",
    Gesture.MOVE:         "Move — pinch drag",
    Gesture.SELECT:       "Select — thumb+pinky",
    Gesture.UNDO:         "Undo — thumb+middle",
    Gesture.REDO:         "Redo — thumb+ring",
    Gesture.SHAPE_RECT:   "Rectangle — V sign",
    Gesture.SHAPE_CIRCLE: "Circle — three fingers",
    Gesture.CLEAR:        "Clear — hold fist",
    Gesture.SAVE:         "Save — rock on",
}

GESTURE_COLORS = {
    Gesture.IDLE:         (160, 160, 160),
    Gesture.DRAW:         (80, 220, 80),
    Gesture.ERASE:        (80, 80, 230),
    Gesture.MOVE:         (220, 180, 80),
    Gesture.SELECT:       (220, 100, 220),
    Gesture.UNDO:         (100, 200, 220),
    Gesture.REDO:         (100, 220, 200),
    Gesture.SHAPE_RECT:   (200, 200, 80),
    Gesture.SHAPE_CIRCLE: (200, 120, 200),
    Gesture.CLEAR:        (60, 60, 220),
    Gesture.SAVE:         (60, 220, 60),
}
