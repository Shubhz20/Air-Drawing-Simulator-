"""
canvas.py - Drawing surface with undo / redo and shape tools
=============================================================
Manages the pixel buffer where all strokes, shapes, and eraser
marks are recorded.  Supports:

  - Freehand drawing with variable brush size
  - Eraser
  - Undo / redo via snapshot stack
  - Shape drawing: rectangles and circles (preview + commit)
  - Save to PNG file
  - Canvas panning via pinch-drag
"""

from __future__ import annotations

import time
from collections import deque
from typing import Optional, Tuple

import cv2
import numpy as np

from config import (
    CANVAS_HEIGHT,
    CANVAS_WIDTH,
    ERASER_RADIUS,
    MAX_UNDO_STEPS,
    SHAPE_MIN_SIZE,
)


class Canvas:
    """
    The drawing surface.

    Internally keeps a stack of image snapshots for undo/redo.
    Drawing operations mutate `self.image` directly for speed;
    undo snapshots are taken at *stroke boundaries* (pen-down / pen-up)
    to avoid blowing up memory.
    """

    def __init__(self, width: int = CANVAS_WIDTH, height: int = CANVAS_HEIGHT):
        self.width = width
        self.height = height

        # Main drawing buffer (black = transparent when composited)
        self.image = np.zeros((height, width, 3), dtype=np.uint8)

        # Undo / redo stacks (store compressed copies to save memory)
        self._undo_stack: deque[bytes] = deque(maxlen=MAX_UNDO_STEPS)
        self._redo_stack: deque[bytes] = deque(maxlen=MAX_UNDO_STEPS)

        # Push the initial blank state so first undo goes to blank
        self._push_undo()

        # Shape preview layer (drawn every frame, not committed until released)
        self._shape_preview: Optional[np.ndarray] = None

    # ── Freehand drawing (with neon glow) ───────

    def draw_line(
        self,
        pt1: Tuple[int, int],
        pt2: Tuple[int, int],
        color: Tuple[int, int, int],
        thickness: int,
        glow: float = 0.6,
    ):
        """
        Draw a smooth neon-glow line segment between two points.
        The glow parameter (0-1) controls how much outer bloom is added.
        """
        # Outer glow layer (thicker, semi-transparent)
        if glow > 0.05:
            glow_layer = self.image.copy()
            cv2.line(
                glow_layer, pt1, pt2, color,
                thickness + int(8 * glow),
                lineType=cv2.LINE_AA,
            )
            alpha = 0.15 + glow * 0.15
            cv2.addWeighted(glow_layer, alpha, self.image, 1 - alpha, 0, self.image)

        # Core bright stroke
        cv2.line(self.image, pt1, pt2, color, thickness, lineType=cv2.LINE_AA)

    def draw_dot(
        self,
        center: Tuple[int, int],
        color: Tuple[int, int, int],
        radius: int,
        glow: float = 0.6,
    ):
        """Draw a single neon dot (used at stroke start and end)."""
        if glow > 0.05:
            glow_layer = self.image.copy()
            cv2.circle(
                glow_layer, center, radius + int(6 * glow),
                color, -1, lineType=cv2.LINE_AA,
            )
            alpha = 0.12 + glow * 0.12
            cv2.addWeighted(glow_layer, alpha, self.image, 1 - alpha, 0, self.image)
        cv2.circle(self.image, center, radius, color, -1, lineType=cv2.LINE_AA)

    # ── Eraser ──────────────────────────────────

    def erase_at(self, center: Tuple[int, int], radius: int = ERASER_RADIUS):
        """Black out a circular region (erase)."""
        cv2.circle(self.image, center, radius, (0, 0, 0), -1)

    # ── Shape drawing ───────────────────────────

    def preview_rectangle(
        self,
        pt1: Tuple[int, int],
        pt2: Tuple[int, int],
        color: Tuple[int, int, int],
        thickness: int,
    ):
        """
        Draw a rectangle preview on a temporary layer.
        Call every frame while the user is sizing the shape.
        """
        self._shape_preview = self.image.copy()
        cv2.rectangle(self._shape_preview, pt1, pt2, color, thickness, lineType=cv2.LINE_AA)

    def preview_circle(
        self,
        center: Tuple[int, int],
        radius: int,
        color: Tuple[int, int, int],
        thickness: int,
    ):
        """Draw a circle preview on a temporary layer."""
        self._shape_preview = self.image.copy()
        cv2.circle(self._shape_preview, center, radius, color, thickness, lineType=cv2.LINE_AA)

    def commit_rectangle(
        self,
        pt1: Tuple[int, int],
        pt2: Tuple[int, int],
        color: Tuple[int, int, int],
        thickness: int,
    ):
        """Permanently draw a rectangle onto the canvas."""
        w = abs(pt2[0] - pt1[0])
        h = abs(pt2[1] - pt1[1])
        if w < SHAPE_MIN_SIZE or h < SHAPE_MIN_SIZE:
            self._shape_preview = None
            return  # too small, discard
        cv2.rectangle(self.image, pt1, pt2, color, thickness, lineType=cv2.LINE_AA)
        self._shape_preview = None

    def commit_circle(
        self,
        center: Tuple[int, int],
        radius: int,
        color: Tuple[int, int, int],
        thickness: int,
    ):
        """Permanently draw a circle onto the canvas."""
        if radius < SHAPE_MIN_SIZE:
            self._shape_preview = None
            return
        cv2.circle(self.image, center, radius, color, thickness, lineType=cv2.LINE_AA)
        self._shape_preview = None

    def get_display_image(self) -> np.ndarray:
        """
        Return the image to composite onto the frame.
        If a shape preview is active, return that; otherwise the base image.
        """
        if self._shape_preview is not None:
            return self._shape_preview
        return self.image

    # ── Canvas panning (pinch-move) ─────────────

    def translate(self, dx: int, dy: int, snapshot: np.ndarray):
        """Shift the entire canvas by (dx, dy) pixels from a snapshot."""
        M = np.float32([[1, 0, dx], [0, 1, dy]])
        self.image = cv2.warpAffine(snapshot, M, (self.width, self.height))

    # ── Undo / Redo ─────────────────────────────

    def save_state(self):
        """
        Take a snapshot of the current canvas for undo.
        Call this at the START of each new stroke / action.
        """
        self._push_undo()
        self._redo_stack.clear()

    def undo(self) -> bool:
        """
        Revert to the previous snapshot.
        Returns True if undo was performed, False if nothing to undo.
        """
        if len(self._undo_stack) < 2:
            return False
        # Current state → redo stack
        current = self._encode(self.image)
        self._redo_stack.append(current)
        # Pop current, then peek at previous
        self._undo_stack.pop()
        prev = self._undo_stack[-1]
        self.image = self._decode(prev)
        return True

    def redo(self) -> bool:
        """
        Re-apply the last undone action.
        Returns True if redo was performed, False if nothing to redo.
        """
        if not self._redo_stack:
            return False
        state = self._redo_stack.pop()
        self._push_undo()
        self.image = self._decode(state)
        return True

    def _push_undo(self):
        self._undo_stack.append(self._encode(self.image))

    @staticmethod
    def _encode(img: np.ndarray) -> bytes:
        """Compress an image to PNG bytes for memory-efficient storage."""
        _, buf = cv2.imencode(".png", img)
        return buf.tobytes()

    @staticmethod
    def _decode(data: bytes) -> np.ndarray:
        """Decompress PNG bytes back to an image array."""
        arr = np.frombuffer(data, dtype=np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)

    # ── Clear / Save ────────────────────────────

    def clear(self):
        """Wipe the canvas. Pushes an undo snapshot first."""
        self.save_state()
        self.image = np.zeros((self.height, self.width, 3), dtype=np.uint8)

    def save(self, directory: str = ".") -> str:
        """
        Save the current drawing as a timestamped PNG.
        Returns the file path.
        """
        filename = f"{directory}/drawing_{int(time.time())}.png"
        cv2.imwrite(filename, self.image)
        return filename

    # ── Compositing ─────────────────────────────

    def composite_onto(self, frame: np.ndarray) -> np.ndarray:
        """
        Overlay the canvas drawing onto a webcam frame.
        Black pixels on the canvas are treated as transparent.
        """
        display = self.get_display_image()

        # Create a mask from non-black canvas pixels
        gray = cv2.cvtColor(display, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 8, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)

        # Combine: frame where canvas is black, canvas where it's not
        bg = cv2.bitwise_and(frame, frame, mask=mask_inv)
        fg = cv2.bitwise_and(display, display, mask=mask)
        return cv2.add(bg, fg)
