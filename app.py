"""
Air Drawing Simulator — Streamlit Cloud Edition
=================================================
Real-time gesture-based drawing using webcam, MediaPipe, and OpenCV.
Deployed via Streamlit Cloud with streamlit-webrtc for webcam access.

Run locally:  streamlit run streamlit_app.py
"""

import time
from collections import deque
from typing import Optional, Tuple

import av
import cv2
import mediapipe as mp
import numpy as np
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, VideoProcessorBase

# ═══════════════════════════════════════════════════
#  PAGE CONFIG
# ═══════════════════════════════════════════════════
st.set_page_config(
    page_title="Air Draw — Gesture-Based Doodler",
    page_icon="✏️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════
#  CUSTOM CSS — Dark neon theme matching reference UI
# ═══════════════════════════════════════════════════
st.markdown("""
<style>
    /* Dark background */
    .stApp { background-color: #0d0d12; }
    [data-testid="stSidebar"] {
        background-color: #14141a;
        border-right: 1px solid #222;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: #ddd !important;
    }

    /* Header styling */
    .main-title {
        font-family: 'Dancing Script', cursive, sans-serif;
        font-size: 42px;
        text-align: center;
        color: #e0e0e0;
        margin-bottom: 0;
        padding-top: 8px;
    }
    .sub-title {
        text-align: center;
        color: #888;
        font-size: 14px;
        margin-bottom: 20px;
    }

    /* Gesture guide cards */
    .gesture-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin: 16px 0;
    }
    .gesture-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px;
        padding: 12px 14px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .gesture-card .emoji { font-size: 24px; }
    .gesture-card .g-title { color: #fff; font-weight: 600; font-size: 14px; }
    .gesture-card .g-desc { color: #888; font-size: 11px; }

    /* Color swatches */
    .color-row {
        display: flex;
        gap: 6px;
        flex-wrap: wrap;
        margin: 8px 0;
    }
    .swatch {
        width: 30px; height: 30px;
        border-radius: 50%;
        display: inline-block;
        border: 2px solid transparent;
    }
    .swatch.active { border-color: #fff; box-shadow: 0 0 8px rgba(255,255,255,0.3); }

    /* Status badge */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(0,0,0,0.4);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px;
        padding: 6px 12px;
        font-size: 13px;
        color: #ccc;
    }
    .status-dot {
        width: 8px; height: 8px;
        border-radius: 50%;
        background: #4ade80;
        display: inline-block;
    }

    /* Hide Streamlit branding */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* WebRTC video container */
    .stVideo > div { border-radius: 12px; overflow: hidden; }
    iframe[title="streamlit_webrtc.component"] {
        border-radius: 12px;
        min-height: 480px;
    }
</style>
<link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════
COLORS = [
    ("Cyan",    (255, 245, 0)),      # BGR
    ("Green",   (68, 255, 34)),
    ("Magenta", (204, 34, 255)),
    ("Blue",    (255, 136, 68)),
    ("Lime",    (0, 255, 170)),
    ("Pink",    (136, 68, 255)),
    ("Yellow",  (0, 221, 255)),
    ("Purple",  (255, 68, 187)),
    ("White",   (255, 255, 255)),
]

COLOR_HEX = [
    "#00fbff", "#00ff00", "#ff00ff", "#0070ff", # Cyan, Green, Magenta, Blue
    "#ff2d55", "#ffcc00", "#af52ff", "#ffffff", # Pink/Red, Yellow, Purple, White
    "#aaff00", # Lime
]

MAX_UNDO = 20
PINCH_THRESHOLD = 0.055


# ═══════════════════════════════════════════════════
#  GESTURE HELPERS
# ═══════════════════════════════════════════════════

def fingers_up(hand_landmarks, handedness="Right"):
    """Return [thumb, index, middle, ring, pinky] booleans."""
    lm = hand_landmarks.landmark
    tips = [4, 8, 12, 16, 20]
    joints = [3, 6, 10, 14, 18]
    result = []
    # Thumb (x-based, adjusted for handedness + mirror flip)
    if handedness == "Right":
        result.append(lm[4].x < lm[3].x)
    else:
        result.append(lm[4].x > lm[3].x)
    # Other fingers (y-based)
    for t, j in zip(tips[1:], joints[1:]):
        result.append(lm[t].y < lm[j].y)
    return result


def pinch_distance(hand_landmarks):
    """Normalised distance between thumb tip and index tip."""
    lm = hand_landmarks.landmark
    dx = lm[4].x - lm[8].x
    dy = lm[4].y - lm[8].y
    return (dx * dx + dy * dy) ** 0.5


def detect_gesture(hand_landmarks, handedness="Right"):
    """Return gesture string from finger pattern."""
    up = fingers_up(hand_landmarks, handedness)
    pd = pinch_distance(hand_landmarks)

    if pd < PINCH_THRESHOLD:
        return "move"
    if up == [False, True, False, False, False]:
        return "draw"
    if all(up):
        return "erase"
    if up == [False, True, True, False, False]:
        return "idle"  # V-sign = pause
    return "idle"


# ═══════════════════════════════════════════════════
#  MEDIAPIPE SETUP
# ═══════════════════════════════════════════════════
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# ═══════════════════════════════════════════════════
#  VIDEO PROCESSOR (runs on each webcam frame)
# ═══════════════════════════════════════════════════

class AirDrawProcessor(VideoProcessorBase):
    """Processes each webcam frame: hand tracking + drawing."""

    def __init__(self):
        # MediaPipe
        self._hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.75,
            min_tracking_confidence=0.70,
        )

        # Canvas
        self.canvas: Optional[np.ndarray] = None
        self._undo_stack: deque = deque(maxlen=MAX_UNDO)
        self._redo_stack: deque = deque(maxlen=MAX_UNDO)

        # Drawing state
        self.color_index = 0
        self.brush_size = 6
        self.glow_amount = 0.6
        self.show_hand = True
        self.prev_point: Optional[Tuple[int, int]] = None
        self.is_drawing = False
        self.is_erasing = False
        self.gesture = "idle"

        # Pointer smoothing
        self._sx: Optional[float] = None
        self._sy: Optional[float] = None
        self._smooth = 0.55

        # Pinch move
        self._pinch_anchor = None
        self._pinch_snap = None

    # ── Smoothing ──
    def _smooth_point(self, x, y):
        if self._sx is None:
            self._sx, self._sy = float(x), float(y)
        else:
            self._sx = self._smooth * self._sx + (1 - self._smooth) * x
            self._sy = self._smooth * self._sy + (1 - self._smooth) * y
        return int(self._sx), int(self._sy)

    def _reset_smooth(self):
        self._sx = self._sy = None

    # ── Undo/Redo ──
    def _push_undo(self):
        if self.canvas is not None:
            _, buf = cv2.imencode(".png", self.canvas)
            self._undo_stack.append(buf.tobytes())
            self._redo_stack.clear()

    def undo(self):
        if len(self._undo_stack) < 2:
            return
        current = cv2.imencode(".png", self.canvas)[1].tobytes()
        self._redo_stack.append(current)
        self._undo_stack.pop()
        prev = self._undo_stack[-1]
        arr = np.frombuffer(prev, dtype=np.uint8)
        self.canvas = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    def redo(self):
        if not self._redo_stack:
            return
        self._push_undo()
        state = self._redo_stack.pop()
        arr = np.frombuffer(state, dtype=np.uint8)
        self.canvas = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    def clear_canvas(self):
        if self.canvas is not None:
            self._push_undo()
            self.canvas = np.zeros_like(self.canvas)

    # ── Neon drawing ──
    def _draw_neon_line(self, pt1, pt2, color, thickness):
        if self.canvas is None:
            return
        # Outer glow
        if self.glow_amount > 0.05:
            glow = self.canvas.copy()
            cv2.line(glow, pt1, pt2, color,
                     thickness + int(8 * self.glow_amount), cv2.LINE_AA)
            a = 0.15 + self.glow_amount * 0.15
            cv2.addWeighted(glow, a, self.canvas, 1 - a, 0, self.canvas)
        # Core stroke
        cv2.line(self.canvas, pt1, pt2, color, thickness, cv2.LINE_AA)

    def _draw_neon_dot(self, center, color, radius):
        if self.canvas is None:
            return
        if self.glow_amount > 0.05:
            glow = self.canvas.copy()
            cv2.circle(glow, center, radius + int(6 * self.glow_amount),
                       color, -1, cv2.LINE_AA)
            a = 0.12 + self.glow_amount * 0.12
            cv2.addWeighted(glow, a, self.canvas, 1 - a, 0, self.canvas)
        cv2.circle(self.canvas, center, radius, color, -1, cv2.LINE_AA)

    # ── Frame processing ──
    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)  # mirror
        h, w = img.shape[:2]

        # Init canvas on first frame
        if self.canvas is None:
            self.canvas = np.zeros((h, w, 3), dtype=np.uint8)
            self._push_undo()

        # Resize canvas if frame size changed
        if self.canvas.shape[:2] != (h, w):
            self.canvas = cv2.resize(self.canvas, (w, h))

        # Hand detection
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self._hands.process(rgb)

        color = COLORS[self.color_index][1]
        self.gesture = "idle"

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            handedness = "Right"
            if results.multi_handedness:
                handedness = results.multi_handedness[0].classification[0].label

            # Draw skeleton
            if self.show_hand:
                mp_draw.draw_landmarks(
                    img, hand, mp_hands.HAND_CONNECTIONS,
                    mp_draw.DrawingSpec(color=(70, 70, 70), thickness=1, circle_radius=2),
                    mp_draw.DrawingSpec(color=(50, 200, 50), thickness=2),
                )

            gesture = detect_gesture(hand, handedness)
            self.gesture = gesture

            # Index fingertip
            lm = hand.landmark[8]
            ix, iy = int(lm.x * w), int(lm.y * h)
            px, py = self._smooth_point(ix, iy)

            # ── DRAW ──
            if gesture == "draw":
                self._pinch_anchor = None
                if not self.is_drawing:
                    self._push_undo()
                    self.is_drawing = True
                    self.prev_point = None
                    self.is_erasing = False
                if self.prev_point is not None:
                    self._draw_neon_line(
                        self.prev_point, (px, py), color, self.brush_size * 2
                    )
                self._draw_neon_dot((px, py), color, self.brush_size)
                self.prev_point = (px, py)

                # Cursor
                overlay = img.copy()
                cv2.circle(overlay, (px, py), self.brush_size + 10, color, -1, cv2.LINE_AA)
                cv2.addWeighted(overlay, 0.12, img, 0.88, 0, img)
                cv2.circle(img, (px, py), self.brush_size + 2, color, 2, cv2.LINE_AA)

            # ── ERASE ──
            elif gesture == "erase":
                self._pinch_anchor = None
                if not self.is_erasing:
                    self._push_undo()
                    self.is_erasing = True
                    self.is_drawing = False
                    self.prev_point = None
                cv2.circle(self.canvas, (px, py), 36, (0, 0, 0), -1)
                cv2.circle(img, (px, py), 36, (100, 100, 255), 2, cv2.LINE_AA)

            # ── MOVE ──
            elif gesture == "move":
                self.prev_point = None
                self.is_drawing = False
                self.is_erasing = False
                tlm = hand.landmark
                mx = int((tlm[4].x + tlm[8].x) / 2 * w)
                my = int((tlm[4].y + tlm[8].y) / 2 * h)
                if self._pinch_anchor is None:
                    self._push_undo()
                    self._pinch_anchor = (mx, my)
                    self._pinch_snap = self.canvas.copy()
                else:
                    dx = mx - self._pinch_anchor[0]
                    dy = my - self._pinch_anchor[1]
                    M = np.float32([[1, 0, dx], [0, 1, dy]])
                    self.canvas = cv2.warpAffine(self._pinch_snap, M, (w, h))
                cv2.drawMarker(img, (mx, my), (255, 200, 80),
                               cv2.MARKER_CROSS, 20, 2, cv2.LINE_AA)

            # ── IDLE ──
            else:
                self.prev_point = None
                self.is_drawing = False
                self.is_erasing = False
                self._pinch_anchor = None
                cv2.circle(img, (px, py), 4, (200, 200, 200), -1, cv2.LINE_AA)
        else:
            self.prev_point = None
            self.is_drawing = False
            self.is_erasing = False
            self._pinch_anchor = None
            self._reset_smooth()

        # ── Composite canvas onto frame ──
        gray = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 8, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        bg = cv2.bitwise_and(img, img, mask=mask_inv)
        fg = cv2.bitwise_and(self.canvas, self.canvas, mask=mask)
        img = cv2.add(bg, fg)

        # ── Camera ON badge ──
        overlay = img.copy()
        cv2.rectangle(overlay, (8, 8), (138, 38), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, img, 0.5, 0, img)
        cv2.circle(img, (24, 23), 4, (128, 224, 80), -1, cv2.LINE_AA)
        cv2.putText(img, "Camera ON", (36, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1, cv2.LINE_AA)

        # ── Gesture label ──
        g_colors = {
            "draw": (80, 220, 80), "erase": (80, 80, 230),
            "move": (220, 180, 80), "idle": (160, 160, 160),
        }
        g_names = {
            "draw": "Draw", "erase": "Erase", "move": "Move", "idle": "Idle",
        }
        gc = g_colors.get(self.gesture, (160, 160, 160))
        gn = g_names.get(self.gesture, "Idle")
        cv2.putText(img, gn, (12, 62),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, gc, 1, cv2.LINE_AA)

        return av.VideoFrame.from_ndarray(img, format="bgr24")


# ═══════════════════════════════════════════════════
#  SIDEBAR UI
# ═══════════════════════════════════════════════════

with st.sidebar:
    st.markdown('<div class="main-title">A</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Air Drawing Simulator</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Gesture guide
    st.markdown("""
    <div class="gesture-grid">
        <div class="gesture-card">
            <span class="emoji">☝️</span>
            <div><div class="g-title">Draw</div><div class="g-desc">Index finger to draw</div></div>
        </div>
        <div class="gesture-card">
            <span class="emoji">✋</span>
            <div><div class="g-title">Erase</div><div class="g-desc">Open palm to erase</div></div>
        </div>
        <div class="gesture-card">
            <span class="emoji">🤏</span>
            <div><div class="g-title">Move</div><div class="g-desc">Pinch to drag</div></div>
        </div>
        <div class="gesture-card">
            <span class="emoji">✌️</span>
            <div><div class="g-title">Idle</div><div class="g-desc">Two fingers to pause</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── COLORS ──
    st.markdown('<div style="text-align:center; font-weight:600; margin-bottom:10px; color:#888; letter-spacing:1px;">COLORS</div>', unsafe_allow_html=True)
    
    selected_color = st.session_state.get("color_index", 0)
    
    # Advanced CSS for glossy circle buttons and active glow
    color_style = "<style>\n"
    for i, (name, _) in enumerate(COLORS):
        hex_val = COLOR_HEX[i]
        is_selected = (i == selected_color)
        
        # Base button styling: Circular, glossy, glowing
        color_style += f"""
        button[title="{name}"] {{
            background: radial-gradient(circle at 30% 30%, {hex_val}, {hex_val}88) !important;
            border-radius: 50% !important;
            width: 45px !important;
            height: 45px !important;
            min-width: 45px !important;
            border: 2px solid {"#ffffff" if is_selected else "transparent"} !important;
            box-shadow: 0 0 {"15px " + hex_val + "aa" if is_selected else "5px " + hex_val + "44"} !important;
            transition: all 0.2s ease-in-out !important;
            margin: 5px auto !important;
            display: block !important;
        }}
        button[title="{name}"] p {{
            display: none !important; /* Hide dot text */
        }}
        button[title="{name}"]:hover {{
            transform: scale(1.1) !important;
            box-shadow: 0 0 20px {hex_val} !important;
            border-color: #ffffffaa !important;
        }}
        """
    color_style += "</style>"
    st.markdown(color_style, unsafe_allow_html=True)

    # Use 4 columns to match the reference screenshot aspect ratio
    color_cols = st.columns(4)
    for i, (name, _) in enumerate(COLORS):
        col = color_cols[i % 4]
        if col.button("", # Empty label, handled by CSS
                      key=f"color_{i}",
                      help=name,
                      use_container_width=False):
            st.session_state["color_index"] = i
            st.rerun()

    # Active color name display
    st.markdown(
        f'<div style="text-align:center; color:{COLOR_HEX[selected_color]}; font-weight:700; font-size:18px; margin-top:10px; text-transform:uppercase; letter-spacing:2px;">'
        f'{COLORS[selected_color][0]}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── THICKNESS ──
    st.markdown("##### THICKNESS")
    brush = st.slider("Brush size", 1, 40, 6, label_visibility="collapsed")

    # ── GLOW ──
    st.markdown("##### GLOW")
    glow = st.slider("Glow amount", 0.0, 1.0, 0.6, 0.05, label_visibility="collapsed")

    st.markdown("---")

    # ── ACTIONS ──
    action_cols = st.columns(3)
    undo_btn = action_cols[0].button("↩ Undo", use_container_width=True)
    clear_btn = action_cols[1].button("🗑 Clear", use_container_width=True)
    save_btn = action_cols[2].button("💾 Save", use_container_width=True)

    st.markdown("---")
    show_hand = st.checkbox("👋 Show hand skeleton", value=True)


# ═══════════════════════════════════════════════════
#  MAIN CANVAS AREA
# ═══════════════════════════════════════════════════

# WebRTC streamer config with dynamic TURN servers
import requests

@st.cache_data(ttl=3600)
def get_ice_servers():
    """Fetch TURN credentials from Metered.ca (cached 1 hour)."""
    try:
        # Using the API Key generated from the Secret Key (Project API Key)
        resp = requests.get(
            "https://techyharshit.metered.live/api/v1/turn/credentials"
            "?apiKey=4180626849e3ff38b099011a05849bbc4ed2",
            timeout=5,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Failed to fetch TURN: {e}")
        return [{"urls": ["stun:stun.l.google.com:19302"]}]

RTC_CONFIGURATION = {
    "iceServers": get_ice_servers()
}

st.markdown("### 🎨 Air Draw Canvas")
st.caption("Click **START** below, allow camera access, then use hand gestures to draw!")

ctx = webrtc_streamer(
    key="air-draw",
    mode=WebRtcMode.SENDRECV,
    video_processor_factory=AirDrawProcessor,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={"video": {"width": 1280, "height": 720}, "audio": False},
    async_processing=True,
)

# Apply sidebar settings to the video processor
if ctx.video_processor:
    ctx.video_processor.color_index = st.session_state.get("color_index", 0)
    ctx.video_processor.brush_size = brush
    ctx.video_processor.glow_amount = glow
    ctx.video_processor.show_hand = show_hand

    if undo_btn:
        ctx.video_processor.undo()
    if clear_btn:
        ctx.video_processor.clear_canvas()
    # Save: grab canvas and offer download
    if save_btn and ctx.video_processor.canvas is not None:
        _, buf = cv2.imencode(".png", ctx.video_processor.canvas)
        st.download_button(
            label="📥 Download Drawing",
            data=buf.tobytes(),
            file_name=f"air_drawing_{int(time.time())}.png",
            mime="image/png",
        )
