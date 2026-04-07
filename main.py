"""
main.py - Air Drawing Simulator entry point
=============================================
Ties together hand tracking, gesture detection, canvas, and UI
into the real-time drawing loop.

Run:
    python main.py

Press Q or close the window to exit.
"""

from __future__ import annotations

import sys
import time
from typing import Optional, Tuple

import cv2
import numpy as np

from config import (
    BRUSH_SIZE_DEFAULT,
    BRUSH_SIZE_MAX,
    BRUSH_SIZE_MIN,
    BRUSH_STEP,
    CAMERA_INDEX,
    CANVAS_HEIGHT,
    CANVAS_WIDTH,
    COLORS,
    ERASER_RADIUS,
    SMOOTHING_FACTOR,
)
from hand_tracker import HandTracker
from gesture_detector import Gesture, GestureDetector
from canvas import Canvas
from ui_overlay import UIOverlay


# ── Pointer smoother ────────────────────────────

class Smoother:
    """
    Exponential moving-average smoother for pointer position.
    Reduces jitter while keeping latency low.
    """

    def __init__(self, factor: float = SMOOTHING_FACTOR):
        self.factor = factor
        self._x: Optional[float] = None
        self._y: Optional[float] = None

    def update(self, x: int, y: int) -> Tuple[int, int]:
        if self._x is None:
            self._x, self._y = float(x), float(y)
        else:
            self._x = self.factor * self._x + (1 - self.factor) * x
            self._y = self.factor * self._y + (1 - self.factor) * y
        return int(self._x), int(self._y)

    def reset(self):
        self._x = self._y = None


# ── Application state ───────────────────────────

class AppState:
    """Mutable application state, passed around the main loop."""

    def __init__(self):
        self.color_index: int = 0
        self.brush_size: int = BRUSH_SIZE_DEFAULT
        self.gesture: Gesture = Gesture.IDLE
        self.prev_point: Optional[Tuple[int, int]] = None

        # For shape drawing
        self.shape_anchor: Optional[Tuple[int, int]] = None

        # For pinch-move
        self.pinch_anchor: Optional[Tuple[int, int]] = None
        self.pinch_snapshot: Optional[np.ndarray] = None

        # Stroke state (to know when to push undo snapshots)
        self.is_drawing: bool = False
        self.is_erasing: bool = False
        self.is_shaping: bool = False

        # Cooldowns to avoid repeated triggers
        self.select_cooldown: float = 0.0
        self.undo_cooldown: float = 0.0
        self.redo_cooldown: float = 0.0
        self.save_cooldown: float = 0.0

    @property
    def color(self) -> Tuple[int, int, int]:
        return COLORS[self.color_index][1]

    def cycle_color(self):
        self.color_index = (self.color_index + 1) % len(COLORS)


# ── Main loop ───────────────────────────────────

def main():
    # ── Initialise components ──
    tracker  = HandTracker(max_hands=1)
    detector = GestureDetector()
    canvas   = Canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    ui       = UIOverlay()
    smoother = Smoother()
    state    = AppState()

    # ── Open webcam ──
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("ERROR: Could not open webcam. Check CAMERA_INDEX in config.py.")
        sys.exit(1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CANVAS_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CANVAS_HEIGHT)

    print("Air Drawing Simulator started!")
    print("Hold up your hand and start drawing. Press Q to quit.\n")

    fps = 0.0
    prev_time = time.time()

    # ────────────────────────────────────────────
    #  MAIN LOOP
    # ────────────────────────────────────────────
    while True:
        ok, frame = cap.read()
        if not ok:
            print("Camera read failed — exiting.")
            break

        # Mirror the frame so it feels like a mirror
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        now = time.time()

        # ── Hand detection ──
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hand_found = tracker.process(rgb)

        pointer: Optional[Tuple[int, int]] = None

        if hand_found:
            # Draw hand skeleton (optional visual aid)
            tracker.draw_skeleton(frame)

            # Read finger states and detect gesture
            fingers = tracker.fingers_up()
            pinch_d = tracker.pinch_distance()
            gesture = detector.detect(fingers, pinch_d, tracker.hand_landmarks)
            state.gesture = gesture

            # Smooth the pointer
            tip = tracker.get_index_tip_px(w, h)
            if tip is not None:
                pointer = smoother.update(*tip)

            # ── Handle each gesture ──
            _handle_gesture(state, gesture, pointer, canvas, ui, tracker, w, h, now)

        else:
            # No hand → reset everything
            state.gesture = Gesture.IDLE
            _end_stroke(state)
            _end_shape(state, canvas)
            _end_pinch(state)
            smoother.reset()

        # ── Composite canvas onto frame ──
        frame = canvas.composite_onto(frame)

        # ── FPS calculation ──
        dt = now - prev_time
        prev_time = now
        fps = 0.9 * fps + 0.1 * (1.0 / max(dt, 1e-6))

        # ── Draw UI ──
        frame = ui.draw(
            frame,
            gesture=state.gesture,
            color_index=state.color_index,
            brush_size=state.brush_size,
            undo_count=len(canvas._undo_stack) - 1,
            redo_count=len(canvas._redo_stack),
            fps=fps,
            pointer=pointer,
            shape_start=state.shape_anchor,
        )

        # ── Show window ──
        cv2.imshow("Air Drawing Simulator | Q = Quit", frame)

        # ── Keyboard controls ──
        key = cv2.waitKey(1) & 0xFF
        _handle_keyboard(key, state, canvas, ui)

        if key == ord("q"):
            break

    # ── Cleanup ──
    cap.release()
    cv2.destroyAllWindows()
    tracker.close()
    print("Air Drawing Simulator closed.")


# ── Gesture handlers ────────────────────────────

def _handle_gesture(
    state: AppState,
    gesture: Gesture,
    pointer: Optional[Tuple[int, int]],
    canvas: Canvas,
    ui: UIOverlay,
    tracker: HandTracker,
    w: int, h: int,
    now: float,
):
    """Route the current gesture to the appropriate drawing logic."""

    if pointer is None:
        return

    px, py = pointer

    # ── DRAW ────────────────────────────────────
    if gesture == Gesture.DRAW:
        _end_shape(state, canvas)
        _end_pinch(state)

        if not state.is_drawing:
            # Stroke started — save undo snapshot
            canvas.save_state()
            state.is_drawing = True
            state.prev_point = None

        if state.prev_point is not None:
            canvas.draw_line(state.prev_point, (px, py), state.color, state.brush_size * 2)
        canvas.draw_dot((px, py), state.color, state.brush_size)
        state.prev_point = (px, py)

    # ── ERASE ───────────────────────────────────
    elif gesture == Gesture.ERASE:
        _end_stroke(state)
        _end_shape(state, canvas)
        _end_pinch(state)

        if not state.is_erasing:
            canvas.save_state()
            state.is_erasing = True

        canvas.erase_at((px, py), ERASER_RADIUS)

    # ── MOVE (pinch drag) ───────────────────────
    elif gesture == Gesture.MOVE:
        _end_stroke(state)
        _end_shape(state, canvas)

        mid = tracker.get_thumb_index_midpoint_px(w, h)
        if mid is not None:
            if state.pinch_anchor is None:
                canvas.save_state()
                state.pinch_anchor = mid
                state.pinch_snapshot = canvas.image.copy()
            else:
                dx = mid[0] - state.pinch_anchor[0]
                dy = mid[1] - state.pinch_anchor[1]
                canvas.translate(dx, dy, state.pinch_snapshot)

    # ── SHAPE_RECT ──────────────────────────────
    elif gesture == Gesture.SHAPE_RECT:
        _end_stroke(state)
        _end_pinch(state)

        if state.shape_anchor is None:
            state.shape_anchor = (px, py)
            state.is_shaping = True
            canvas.save_state()
        else:
            canvas.preview_rectangle(
                state.shape_anchor, (px, py), state.color, state.brush_size * 2,
            )

    # ── SHAPE_CIRCLE ────────────────────────────
    elif gesture == Gesture.SHAPE_CIRCLE:
        _end_stroke(state)
        _end_pinch(state)

        if state.shape_anchor is None:
            state.shape_anchor = (px, py)
            state.is_shaping = True
            canvas.save_state()
        else:
            radius = int(np.hypot(px - state.shape_anchor[0], py - state.shape_anchor[1]))
            canvas.preview_circle(
                state.shape_anchor, radius, state.color, state.brush_size * 2,
            )

    # ── SELECT (cycle colour) ───────────────────
    elif gesture == Gesture.SELECT:
        _end_stroke(state)
        _end_pinch(state)
        # Commit any in-progress shape before switching colour
        _end_shape(state, canvas)

        if now - state.select_cooldown > 0.8:
            state.cycle_color()
            ui.flash(f"Colour: {COLORS[state.color_index][0]}", state.color)
            state.select_cooldown = now

    # ── UNDO ────────────────────────────────────
    elif gesture == Gesture.UNDO:
        _end_stroke(state)
        _end_shape(state, canvas)
        _end_pinch(state)

        if now - state.undo_cooldown > 0.6:
            if canvas.undo():
                ui.flash("Undo", (100, 200, 220))
            state.undo_cooldown = now

    # ── REDO ────────────────────────────────────
    elif gesture == Gesture.REDO:
        _end_stroke(state)
        _end_shape(state, canvas)
        _end_pinch(state)

        if now - state.redo_cooldown > 0.6:
            if canvas.redo():
                ui.flash("Redo", (100, 220, 200))
            state.redo_cooldown = now

    # ── SAVE ────────────────────────────────────
    elif gesture == Gesture.SAVE:
        _end_stroke(state)
        _end_shape(state, canvas)
        _end_pinch(state)

        if now - state.save_cooldown > 2.0:
            path = canvas.save()
            ui.flash(f"Saved!", (60, 220, 60))
            print(f"Drawing saved to {path}")
            state.save_cooldown = now

    # ── CLEAR ───────────────────────────────────
    elif gesture == Gesture.CLEAR:
        _end_stroke(state)
        _end_shape(state, canvas)
        _end_pinch(state)

        canvas.clear()
        ui.flash("Canvas Cleared", (60, 60, 220))

    # ── IDLE ────────────────────────────────────
    else:
        # Commit any in-progress shape when user lifts fingers
        if state.is_shaping and state.shape_anchor is not None:
            _commit_shape(state, canvas, px, py)
        _end_stroke(state)
        _end_pinch(state)


# ── Stroke / shape lifecycle helpers ────────────

def _end_stroke(state: AppState):
    """Called when the user stops drawing."""
    state.prev_point = None
    state.is_drawing = False
    state.is_erasing = False

def _end_shape(state: AppState, canvas: Canvas):
    """Discard shape preview without committing."""
    state.shape_anchor = None
    state.is_shaping = False
    canvas._shape_preview = None

def _commit_shape(state: AppState, canvas: Canvas, px: int, py: int):
    """Finalise the current shape onto the canvas."""
    if state.shape_anchor is None:
        return
    anchor = state.shape_anchor

    if state.gesture == Gesture.SHAPE_RECT or state.gesture == Gesture.IDLE:
        # If we transitioned to IDLE from SHAPE_RECT, commit rectangle
        canvas.commit_rectangle(anchor, (px, py), state.color, state.brush_size * 2)
    elif state.gesture == Gesture.SHAPE_CIRCLE:
        radius = int(np.hypot(px - anchor[0], py - anchor[1]))
        canvas.commit_circle(anchor, radius, state.color, state.brush_size * 2)

    state.shape_anchor = None
    state.is_shaping = False

def _end_pinch(state: AppState):
    """Reset pinch-move state."""
    state.pinch_anchor = None
    state.pinch_snapshot = None


# ── Keyboard handler ────────────────────────────

def _handle_keyboard(key: int, state: AppState, canvas: Canvas, ui: UIOverlay):
    """Process keyboard shortcuts."""

    if key == ord("c"):
        canvas.clear()
        ui.flash("Canvas Cleared", (60, 60, 220))

    elif key == ord("s"):
        path = canvas.save()
        ui.flash("Saved!", (60, 220, 60))
        print(f"Drawing saved to {path}")

    elif key == ord("z"):
        if canvas.undo():
            ui.flash("Undo", (100, 200, 220))

    elif key == ord("y"):
        if canvas.redo():
            ui.flash("Redo", (100, 220, 200))

    elif key in (ord("+"), ord("=")):
        state.brush_size = min(state.brush_size + BRUSH_STEP, BRUSH_SIZE_MAX)

    elif key == ord("-"):
        state.brush_size = max(state.brush_size - BRUSH_STEP, BRUSH_SIZE_MIN)

    # Number keys 1-8 select colour
    for i in range(min(len(COLORS), 8)):
        if key == ord(str(i + 1)):
            state.color_index = i
            ui.flash(f"Colour: {COLORS[i][0]}", COLORS[i][1])
            break


# ── Entry point ─────────────────────────────────

if __name__ == "__main__":
    main()
