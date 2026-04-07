"""
hand_tracker.py - MediaPipe hand detection wrapper
====================================================
Encapsulates MediaPipe Hands so the rest of the app only deals with
simple Python objects (landmark lists, pixel coordinates, etc.).

MediaPipe detects 21 3-D landmarks per hand:
    0  = wrist
    1-4   = thumb  (CMC → TIP)
    5-8   = index  (MCP → TIP)
    9-12  = middle (MCP → TIP)
    13-16 = ring   (MCP → TIP)
    17-20 = pinky  (MCP → TIP)

Each landmark has normalised (x, y, z) where x/y are in [0, 1]
relative to the image and z represents depth (negative = closer).
"""

import mediapipe as mp
import numpy as np


class HandTracker:
    """Thin wrapper around MediaPipe Hands."""

    # Landmark indices for fingertips and the joint just below them
    TIP_IDS   = [4, 8, 12, 16, 20]   # thumb, index, middle, ring, pinky
    JOINT_IDS = [3, 6, 10, 14, 18]   # joint one below each tip

    def __init__(
        self,
        max_hands: int = 1,
        detection_confidence: float = 0.75,
        tracking_confidence: float = 0.70,
    ):
        self._mp_hands = mp.solutions.hands
        self._mp_draw  = mp.solutions.drawing_utils

        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )

        # Cache the latest results so callers don't hold MediaPipe internals
        self._results = None

    # ── public API ──────────────────────────────────

    def process(self, rgb_frame: np.ndarray):
        """
        Run hand detection on an RGB frame.
        Returns True if at least one hand was detected.
        """
        self._results = self._hands.process(rgb_frame)
        return self._results.multi_hand_landmarks is not None

    @property
    def hand_landmarks(self):
        """Return the first detected hand's landmark object (or None)."""
        if self._results and self._results.multi_hand_landmarks:
            return self._results.multi_hand_landmarks[0]
        return None

    @property
    def handedness(self) -> str:
        """Return 'Left' or 'Right' for the first detected hand."""
        if self._results and self._results.multi_handedness:
            return self._results.multi_handedness[0].classification[0].label
        return "Right"  # default assumption

    def get_landmark_px(self, landmark_id: int, frame_w: int, frame_h: int):
        """
        Return (x, y) pixel coordinates for a single landmark.
        Returns None if no hand is detected.
        """
        hand = self.hand_landmarks
        if hand is None:
            return None
        lm = hand.landmark[landmark_id]
        return int(lm.x * frame_w), int(lm.y * frame_h)

    def get_all_landmarks_px(self, frame_w: int, frame_h: int):
        """
        Return a list of 21 (x, y) tuples in pixel space,
        or None if no hand is detected.
        """
        hand = self.hand_landmarks
        if hand is None:
            return None
        return [
            (int(lm.x * frame_w), int(lm.y * frame_h))
            for lm in hand.landmark
        ]

    def get_index_tip_px(self, frame_w: int, frame_h: int):
        """Convenience: pixel coords of the index fingertip (landmark 8)."""
        return self.get_landmark_px(8, frame_w, frame_h)

    def get_thumb_tip_px(self, frame_w: int, frame_h: int):
        """Convenience: pixel coords of the thumb tip (landmark 4)."""
        return self.get_landmark_px(4, frame_w, frame_h)

    def get_thumb_index_midpoint_px(self, frame_w: int, frame_h: int):
        """Midpoint between thumb tip and index tip in pixels."""
        thumb = self.get_thumb_tip_px(frame_w, frame_h)
        index = self.get_index_tip_px(frame_w, frame_h)
        if thumb is None or index is None:
            return None
        return (thumb[0] + index[0]) // 2, (thumb[1] + index[1]) // 2

    def fingers_up(self) -> list[bool]:
        """
        Returns [thumb, index, middle, ring, pinky] booleans.
        True = finger is extended.  Handles left/right hand mirroring.
        """
        hand = self.hand_landmarks
        if hand is None:
            return [False] * 5

        lm = hand.landmark
        result = []

        # Thumb:  compare x-positions, direction depends on handedness.
        # Because the webcam image is already flipped horizontally,
        # "Right" hand in MediaPipe actually appears on the left side
        # of the screen, so we invert the comparison.
        if self.handedness == "Right":
            result.append(lm[4].x < lm[3].x)   # tip left of joint
        else:
            result.append(lm[4].x > lm[3].x)   # tip right of joint

        # Index → pinky: tip above (lower y than) the PIP joint
        for tip, joint in zip(self.TIP_IDS[1:], self.JOINT_IDS[1:]):
            result.append(lm[tip].y < lm[joint].y)

        return result

    def pinch_distance(self) -> float:
        """
        Normalised Euclidean distance between thumb tip and index tip.
        Ranges roughly 0.0 (touching) to ~0.3 (spread wide).
        """
        hand = self.hand_landmarks
        if hand is None:
            return 1.0  # large = no pinch
        lm = hand.landmark
        dx = lm[4].x - lm[8].x
        dy = lm[4].y - lm[8].y
        return (dx * dx + dy * dy) ** 0.5

    # ── drawing helpers ─────────────────────────────

    def draw_skeleton(self, frame: np.ndarray):
        """
        Draw the hand skeleton (landmarks + connections) on the frame.
        Useful for debugging; can be toggled off in production.
        """
        hand = self.hand_landmarks
        if hand is None:
            return
        self._mp_draw.draw_landmarks(
            frame,
            hand,
            self._mp_hands.HAND_CONNECTIONS,
            self._mp_draw.DrawingSpec(
                color=(70, 70, 70), thickness=1, circle_radius=2
            ),
            self._mp_draw.DrawingSpec(
                color=(50, 200, 50), thickness=2
            ),
        )

    # ── cleanup ─────────────────────────────────────

    def close(self):
        self._hands.close()
