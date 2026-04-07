"""
config.py - Central configuration for Air Drawing Simulator
============================================================
All tweakable settings in one place. Adjust these to fit your
webcam, lighting, and drawing preferences.
"""

# ── Camera ──────────────────────────────────────
CAMERA_INDEX = 0            # 0 = default webcam; change if you have multiple
CANVAS_WIDTH = 1280         # output window width  (px)
CANVAS_HEIGHT = 720         # output window height (px)
FPS_TARGET = 30             # desired frame rate

# ── Brush ───────────────────────────────────────
BRUSH_SIZE_DEFAULT = 6      # starting brush radius (px)
BRUSH_SIZE_MIN = 1
BRUSH_SIZE_MAX = 40
BRUSH_STEP = 2              # increment per +/- key press

# ── Eraser ──────────────────────────────────────
ERASER_RADIUS = 36          # eraser circle radius (px)

# ── Smoothing ───────────────────────────────────
# Exponential moving average factor for pointer position.
# 0.0 = raw (jittery), 0.9 = extremely smooth (laggy).
# Range 0.4 – 0.65 works well for most people.
SMOOTHING_FACTOR = 0.55

# ── Gesture thresholds ──────────────────────────
PINCH_THRESHOLD = 0.055     # normalised distance between thumb & index tips
FINGER_BEND_THRESHOLD = 0.04  # how much a finger must bend to count as "down"

# ── Colour palette (BGR for OpenCV) ─────────────
COLORS = [
    ("Red",     (60,  60,  230)),
    ("Blue",    (230, 120, 50)),
    ("Green",   (80,  200, 80)),
    ("Yellow",  (40,  230, 230)),
    ("White",   (240, 240, 240)),
    ("Magenta", (200, 80,  200)),
    ("Cyan",    (220, 200, 40)),
    ("Orange",  (40,  140, 240)),
]

# ── Undo / Redo ─────────────────────────────────
MAX_UNDO_STEPS = 30         # how many snapshots we keep in the undo stack

# ── Shape drawing ───────────────────────────────
SHAPE_MIN_SIZE = 15         # minimum pixel dimension to register a shape

# ── UI layout ───────────────────────────────────
TOOLBAR_HEIGHT = 60         # top toolbar height (px)
TOOLBAR_ALPHA = 0.65        # toolbar transparency  (0 = invisible, 1 = opaque)
STATUS_BAR_HEIGHT = 32      # bottom status bar
BUTTON_RADIUS = 20          # colour swatch radius
BUTTON_SPACING = 52         # spacing between toolbar buttons
