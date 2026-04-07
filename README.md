# Air Drawing Simulator

Draw in the air using hand gestures detected by your webcam. No mouse, no stylus — just your hand.

Built with **Python**, **OpenCV**, and **MediaPipe**.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-green)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10%2B-orange)

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python main.py
```

A window opens with your webcam feed. Hold up your hand and start drawing!

---

## Gestures

| Gesture | Fingers | Action |
|---|---|---|
| Index finger only | ☝️ | **Draw** — follow your fingertip |
| Open palm (all 5) | ✋ | **Erase** — rub out strokes |
| Pinch (thumb+index) | 🤏 | **Move** — drag the whole canvas |
| V sign (index+middle) | ✌️ | **Rectangle** — draw shape |
| Three fingers (I+M+R) | 🖖 | **Circle** — draw shape |
| Thumb + pinky | 🤙 | **Cycle colour** |
| Thumb + middle | | **Undo** |
| Thumb + ring | | **Redo** |
| Fist (hold 1.5s) | ✊ | **Clear canvas** |
| Thumb + index + pinky | 🤟 | **Save drawing** |

---

## Keyboard Shortcuts

| Key | Action |
|---|---|
| `1`–`8` | Switch colour |
| `+` / `-` | Increase / decrease brush size |
| `C` | Clear canvas |
| `S` | Save drawing as PNG |
| `Z` | Undo |
| `Y` | Redo |
| `Q` | Quit |

---

## Project Structure

```
AIR-DRAWING-SIMULATOR/
├── main.py              # Application entry point & main loop
├── config.py            # All settings in one place
├── hand_tracker.py      # MediaPipe hand detection wrapper
├── gesture_detector.py  # Rule-based & ML gesture recognition
├── canvas.py            # Drawing surface + undo/redo + shapes
├── ui_overlay.py        # On-screen HUD and toolbar
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

---

## How It Works

### 1. Hand Tracking (MediaPipe)

MediaPipe's Hand solution detects **21 3D landmarks** per hand in real time. Each landmark has normalised (x, y, z) coordinates. The model runs a two-stage pipeline: first a palm detector locates the hand bounding box, then a landmark model predicts the 21 joint positions within that box.

### 2. Gesture Detection

Gestures are recognised by checking which fingers are "up" (extended). For each finger, we compare the y-coordinate of the fingertip landmark against the joint just below it — if the tip is higher (smaller y), the finger is extended. The thumb uses x-coordinate comparison instead, adjusted for handedness.

Different finger combinations map to different actions (see the gesture table above). A pinch is detected when the Euclidean distance between thumb tip and index tip falls below a threshold.

### 3. Drawing Logic

When the DRAW gesture is active, the app tracks the index fingertip position through an **exponential moving average** smoother to reduce jitter. It draws thick line segments between consecutive frames using OpenCV's `cv2.line()` with anti-aliasing, plus dots at each point for smooth stroke caps.

The canvas is a separate black image that gets **composited** onto the webcam frame each loop — black pixels are treated as transparent, so only the drawn strokes appear overlaid on the video.

### 4. Undo/Redo

Canvas snapshots are **PNG-compressed** and stored in a deque. Snapshots are taken at stroke boundaries (when you start a new stroke), not every frame, keeping memory usage reasonable while still allowing fine-grained undo.

### 5. Shape Drawing

Rectangle and circle tools use a two-phase approach: while you hold the gesture, a **preview** is rendered on a temporary layer each frame. When you release (switch to IDLE), the shape is **committed** to the permanent canvas.

---

## Configuration

All settings are in `config.py`. Key ones:

| Setting | Default | Description |
|---|---|---|
| `CAMERA_INDEX` | 0 | Webcam device index |
| `CANVAS_WIDTH` | 1280 | Window width |
| `CANVAS_HEIGHT` | 720 | Window height |
| `SMOOTHING_FACTOR` | 0.55 | Pointer smoothing (0=raw, 0.9=very smooth) |
| `BRUSH_SIZE_DEFAULT` | 6 | Starting brush radius |
| `PINCH_THRESHOLD` | 0.055 | Pinch detection sensitivity |

---

## Possible Improvements

- **Pressure sensitivity** — use the z-coordinate (depth) of the fingertip to vary brush width
- **Multi-hand support** — let two people draw simultaneously
- **Colour picker wheel** — gesture to open a radial colour picker
- **Export as SVG** — record stroke paths as vectors instead of rasterised pixels
- **Network mode** — stream the canvas over WebSocket for collaborative drawing
- **ML gesture classifier** — the `gesture_detector.py` module already has scaffolding for training a Random Forest on collected landmark data

---

## License

MIT — do whatever you like with it.
