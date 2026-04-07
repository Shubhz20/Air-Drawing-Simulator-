"""
ui_overlay.py - On-screen heads-up display matching the reference UI
=====================================================================
Right-side floating panel with colour swatches, thickness/glow sliders,
and action icons.  "Camera ON" badge top-left.  "SHOW HAND" toggle
bottom-centre.  Neon-glow cursor.

All rendering done with OpenCV drawing primitives and alpha compositing.
"""

from __future__ import annotations

from typing import Optional, Tuple

import cv2
import numpy as np

from config import (
    BUTTON_RADIUS,
    COLORS,
    ERASER_RADIUS,
)
from gesture_detector import (
    Gesture,
    GESTURE_COLORS,
    GESTURE_DESCRIPTIONS,
)


class UIOverlay:
    """Renders the HUD on each frame — styled to match the reference app."""

    FLASH_DURATION = 60   # frames (~2 s at 30 fps)

    # Sidebar geometry
    PANEL_W = 160
    PANEL_PAD = 16
    PANEL_RADIUS = 14
    SWATCH_R = 12
    SWATCH_GAP = 8
    ICON_SIZE = 36

    def __init__(self):
        self._flash_text: Optional[str] = None
        self._flash_frames: int = 0
        self._flash_color: Tuple[int, int, int] = (80, 220, 80)
        self.show_hand: bool = True

    # ── Flash messages ──────────────────────────

    def flash(self, text: str, color: Tuple[int, int, int] = (80, 220, 80)):
        self._flash_text = text
        self._flash_frames = self.FLASH_DURATION
        self._flash_color = color

    def _tick_flash(self):
        if self._flash_frames > 0:
            self._flash_frames -= 1
        else:
            self._flash_text = None

    # ── Helpers ─────────────────────────────────

    @staticmethod
    def _rounded_rect(img, pt1, pt2, color, radius, alpha=0.75):
        """Draw a rounded rectangle with alpha blending."""
        overlay = img.copy()
        x1, y1 = pt1
        x2, y2 = pt2
        # Draw filled rect (corners not truly rounded in OpenCV,
        # but the visual approximation is fine at small radii)
        cv2.rectangle(overlay, (x1 + radius, y1), (x2 - radius, y2), color, -1)
        cv2.rectangle(overlay, (x1, y1 + radius), (x2, y2 - radius), color, -1)
        cv2.circle(overlay, (x1 + radius, y1 + radius), radius, color, -1)
        cv2.circle(overlay, (x2 - radius, y1 + radius), radius, color, -1)
        cv2.circle(overlay, (x1 + radius, y2 - radius), radius, color, -1)
        cv2.circle(overlay, (x2 - radius, y2 - radius), radius, color, -1)
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

    # ── Main render ─────────────────────────────

    def draw(
        self,
        frame: np.ndarray,
        gesture: Gesture,
        color_index: int,
        brush_size: int,
        undo_count: int,
        redo_count: int,
        fps: float,
        pointer: Optional[Tuple[int, int]] = None,
        shape_start: Optional[Tuple[int, int]] = None,
    ) -> np.ndarray:
        h, w = frame.shape[:2]
        active_color = COLORS[color_index][1]

        # ── "Camera ON" badge (top-left) ──
        self._rounded_rect(
            frame, (12, 10), (140, 42), (0, 0, 0), 6, alpha=0.5,
        )
        # Green dot
        cv2.circle(frame, (28, 26), 4, (128, 224, 80), -1, cv2.LINE_AA)
        cv2.putText(
            frame, "Camera ON", (40, 31),
            cv2.FONT_HERSHEY_SIMPLEX, 0.48, (200, 200, 200), 1, cv2.LINE_AA,
        )

        # ── Right sidebar panel ──
        panel_x = w - self.PANEL_W - 20
        panel_y1 = h // 2 - 240
        panel_y2 = h // 2 + 240
        self._rounded_rect(
            frame,
            (panel_x, panel_y1), (w - 20, panel_y2),
            (20, 20, 25), self.PANEL_RADIUS, alpha=0.78,
        )

        cx = panel_x + self.PANEL_W // 2  # centre x of panel

        # "COLORS" label
        y = panel_y1 + 24
        cv2.putText(
            frame, "COLORS", (cx - 28, y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.38, (136, 136, 136), 1, cv2.LINE_AA,
        )
        y += 16

        # Colour swatches (2 rows of 5)
        for row in range(2):
            for col in range(5):
                idx = row * 5 + col
                if idx >= len(COLORS):
                    break
                sx = panel_x + 22 + col * (self.SWATCH_R * 2 + self.SWATCH_GAP)
                sy = y + row * (self.SWATCH_R * 2 + self.SWATCH_GAP)
                bgr = COLORS[idx][1]
                cv2.circle(frame, (sx, sy), self.SWATCH_R, bgr, -1, cv2.LINE_AA)
                if idx == color_index:
                    cv2.circle(frame, (sx, sy), self.SWATCH_R + 3, (255, 255, 255), 2, cv2.LINE_AA)

        y += 2 * (self.SWATCH_R * 2 + self.SWATCH_GAP) + 10

        # "THICKNESS" label
        cv2.putText(
            frame, "THICKNESS", (cx - 40, y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (136, 136, 136), 1, cv2.LINE_AA,
        )
        y += 14

        # Neon star (big dot in active colour)
        cv2.circle(frame, (cx, y + 6), 14, active_color, -1, cv2.LINE_AA)
        # Glow effect
        overlay = frame.copy()
        cv2.circle(overlay, (cx, y + 6), 22, active_color, -1, cv2.LINE_AA)
        cv2.addWeighted(overlay, 0.15, frame, 0.85, 0, frame)
        y += 28

        # Thickness slider bar
        bar_x1 = panel_x + 24
        bar_x2 = w - 44
        bar_y = y
        cv2.line(frame, (bar_x1, bar_y), (bar_x2, bar_y), (60, 60, 60), 3, cv2.LINE_AA)
        pct = (brush_size - 1) / 39.0
        thumb_x = int(bar_x1 + pct * (bar_x2 - bar_x1))
        cv2.circle(frame, (thumb_x, bar_y), 6, (255, 255, 255), -1, cv2.LINE_AA)
        y += 14
        cv2.putText(
            frame, f"{brush_size}px", (cx - 12, y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (100, 100, 100), 1, cv2.LINE_AA,
        )
        y += 22

        # "GLOW" label
        cv2.putText(
            frame, "GLOW", (cx - 18, y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (136, 136, 136), 1, cv2.LINE_AA,
        )
        y += 14
        # Glow slider
        cv2.line(frame, (bar_x1, y), (bar_x2, y), (60, 60, 60), 3, cv2.LINE_AA)
        glow_x = int(bar_x1 + 0.6 * (bar_x2 - bar_x1))
        cv2.circle(frame, (glow_x, y), 6, (255, 255, 255), -1, cv2.LINE_AA)
        y += 14
        cv2.putText(
            frame, "60%", (cx - 12, y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (100, 100, 100), 1, cv2.LINE_AA,
        )
        y += 18

        # Divider
        cv2.line(
            frame, (panel_x + 20, y), (w - 40, y),
            (50, 50, 55), 1, cv2.LINE_AA,
        )
        y += 16

        # Icon buttons: undo, clear, eraser, download
        icons = ["Undo", "Clear", "Eraser", "Save"]
        for i, label in enumerate(icons):
            iy = y + i * (self.ICON_SIZE + 8)
            # Button background
            btn_x1 = cx - self.ICON_SIZE // 2
            btn_y1 = iy - self.ICON_SIZE // 2
            btn_x2 = cx + self.ICON_SIZE // 2
            btn_y2 = iy + self.ICON_SIZE // 2
            self._rounded_rect(
                frame, (btn_x1, btn_y1), (btn_x2, btn_y2),
                (40, 40, 45), 8, alpha=0.5,
            )
            cv2.putText(
                frame, label[0], (cx - 5, iy + 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 160, 160), 1, cv2.LINE_AA,
            )

        # ── Gesture label (top-left under camera badge) ──
        g_color = GESTURE_COLORS.get(gesture, (200, 200, 200))
        g_text = GESTURE_DESCRIPTIONS.get(gesture, str(gesture))
        cv2.putText(
            frame, g_text, (14, 66),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, g_color, 1, cv2.LINE_AA,
        )

        # ── Bottom "SHOW HAND" toggle ──
        toggle_text = "SHOW HAND" if self.show_hand else "HIDE HAND"
        tw = cv2.getTextSize(toggle_text, cv2.FONT_HERSHEY_SIMPLEX, 0.48, 1)[0][0]
        tx = w // 2 - tw // 2 - 16
        self._rounded_rect(
            frame, (tx - 14, h - 48), (tx + tw + 30, h - 14),
            (20, 20, 25), 16, alpha=0.65,
        )
        cv2.putText(
            frame, toggle_text, (tx + 10, h - 26),
            cv2.FONT_HERSHEY_SIMPLEX, 0.48, (187, 187, 187), 1, cv2.LINE_AA,
        )

        # ── FPS (bottom-left, subtle) ──
        cv2.putText(
            frame, f"FPS: {fps:.0f}", (14, h - 16),
            cv2.FONT_HERSHEY_SIMPLEX, 0.38, (80, 140, 80), 1, cv2.LINE_AA,
        )

        # ── Pointer cursor with neon glow ──
        if pointer is not None:
            px, py = pointer
            if gesture == Gesture.DRAW:
                # Outer glow
                overlay = frame.copy()
                cv2.circle(overlay, (px, py), brush_size + 10, active_color, -1, cv2.LINE_AA)
                cv2.addWeighted(overlay, 0.12, frame, 0.88, 0, frame)
                # Inner ring
                cv2.circle(frame, (px, py), brush_size + 2, active_color, 2, cv2.LINE_AA)
                cv2.circle(frame, (px, py), 2, (255, 255, 255), -1, cv2.LINE_AA)
            elif gesture == Gesture.ERASE:
                cv2.circle(frame, (px, py), ERASER_RADIUS, (100, 100, 255), 2, cv2.LINE_AA)
            elif gesture == Gesture.MOVE:
                cv2.drawMarker(
                    frame, (px, py), (255, 200, 80),
                    cv2.MARKER_CROSS, 20, 2, cv2.LINE_AA,
                )
            elif gesture in (Gesture.SHAPE_RECT, Gesture.SHAPE_CIRCLE):
                cv2.circle(frame, (px, py), 5, (200, 200, 80), -1, cv2.LINE_AA)
            else:
                cv2.circle(frame, (px, py), 4, (200, 200, 200), -1, cv2.LINE_AA)

        # ── Shape anchor crosshair ──
        if shape_start is not None:
            sx, sy = shape_start
            cv2.drawMarker(
                frame, (sx, sy), (200, 200, 80),
                cv2.MARKER_TILTED_CROSS, 12, 1, cv2.LINE_AA,
            )

        # ── Flash message (centre, with neon text shadow) ──
        if self._flash_text is not None:
            text_size = cv2.getTextSize(
                self._flash_text, cv2.FONT_HERSHEY_SIMPLEX, 1.6, 3
            )[0]
            ftx = (w - text_size[0]) // 2
            fty = h // 2 + text_size[1] // 2
            # Glow
            overlay = frame.copy()
            cv2.putText(
                overlay, self._flash_text, (ftx, fty),
                cv2.FONT_HERSHEY_SIMPLEX, 1.6, self._flash_color, 8, cv2.LINE_AA,
            )
            cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
            # Core text
            cv2.putText(
                frame, self._flash_text, (ftx, fty),
                cv2.FONT_HERSHEY_SIMPLEX, 1.6, self._flash_color, 3, cv2.LINE_AA,
            )
            self._tick_flash()

        return frame
