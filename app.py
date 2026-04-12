"""
Air Drawing Simulator — Streamlit Cloud Edition
=================================================
Embeds the pure-frontend air drawing app inside Streamlit.
Camera runs in-browser via getUserMedia (no WebRTC/STUN needed).
Hand tracking via MediaPipe JS Tasks Vision API.
"""

import streamlit as st

st.set_page_config(
    page_title="Air Draw — Gesture Drawing",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide Streamlit chrome for fullscreen experience
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp > header {display: none;}
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    [data-testid="stAppViewContainer"] {
        padding: 0;
    }
    iframe {
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# The entire app runs client-side in this HTML component
AIR_DRAW_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Dancing+Script:wght@700&display=swap');

    * { margin: 0; padding: 0; box-sizing: border-box; }

    body, html {
        background: #0a0a0f;
        color: #e0e0e0;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
        overflow: hidden;
        height: 100%;
        width: 100%;
        cursor: crosshair;
    }

    .container {
        position: relative;
        width: 100%;
        height: 100%;
        overflow: hidden;
    }

    #webcam {
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        object-fit: cover;
        z-index: 1;
        transform: scaleX(-1);
    }

    #drawCanvas {
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        z-index: 2;
        cursor: crosshair;
    }

    .camera-badge {
        position: absolute;
        top: 12px; left: 12px;
        z-index: 10;
        background: rgba(0,0,0,0.5);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px;
        padding: 6px 12px;
        font-size: 12px;
        font-weight: 500;
        color: #ccc;
        display: flex;
        align-items: center;
        gap: 7px;
    }

    .status-dot {
        width: 7px; height: 7px;
        border-radius: 50%;
        background: #4ade80;
        box-shadow: 0 0 6px #4ade80;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
    }

    .sidebar {
        position: absolute;
        top: 50%; right: 12px;
        transform: translateY(-50%);
        z-index: 10;
        background: rgba(18,18,22,0.85);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 16px 12px;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
        width: 160px;
    }

    .sidebar-label {
        font-size: 10px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #888;
        width: 100%;
        text-align: center;
    }

    .color-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 5px;
        width: 100%;
        justify-items: center;
    }

    .color-dot {
        width: 24px; height: 24px;
        border-radius: 50%;
        cursor: pointer;
        border: 2px solid transparent;
        transition: all 0.15s;
    }
    .color-dot:hover { transform: scale(1.2); }
    .color-dot.active {
        border-color: #fff;
        box-shadow: 0 0 10px rgba(255,255,255,0.3);
        transform: scale(1.15);
    }

    .neon-star {
        font-size: 24px;
        filter: drop-shadow(0 0 6px currentColor);
    }

    .slider-section {
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;
    }

    .slider {
        width: 80%; height: 3px;
        background: rgba(255,255,255,0.1);
        border-radius: 4px;
        outline: none;
        -webkit-appearance: none;
        appearance: none;
        cursor: pointer;
    }
    .slider::-webkit-slider-thumb {
        -webkit-appearance: none;
        width: 12px; height: 12px;
        border-radius: 50%;
        background: #fff;
        box-shadow: 0 0 4px rgba(255,255,255,0.4);
        cursor: grab;
    }

    .slider-value { font-size: 10px; color: #666; }

    .divider {
        width: 80%; height: 1px;
        background: rgba(255,255,255,0.07);
    }

    .icon-row {
        display: flex;
        gap: 6px;
        width: 100%;
        justify-content: center;
        flex-wrap: wrap;
    }

    .icon-btn {
        width: 36px; height: 36px;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.08);
        background: rgba(255,255,255,0.04);
        color: #999;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.15s;
        font-size: 16px;
        padding: 0;
    }
    .icon-btn:hover {
        background: rgba(255,255,255,0.1);
        color: #fff;
    }
    .icon-btn.active-tool {
        background: rgba(255,100,100,0.15);
        border-color: rgba(255,100,100,0.3);
        color: #ff6666;
    }

    .bottom-bar {
        position: absolute;
        bottom: 16px; left: 50%;
        transform: translateX(-50%);
        z-index: 10;
        display: flex; gap: 8px;
    }

    .bottom-btn {
        background: rgba(18,18,22,0.8);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 24px;
        padding: 8px 18px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
        color: #bbb;
        cursor: pointer;
        transition: all 0.2s;
        font-family: inherit;
    }
    .bottom-btn:hover { background: rgba(30,30,35,0.9); color: #fff; }

    .flash-msg {
        position: fixed;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        font-size: 32px;
        font-weight: 700;
        pointer-events: none;
        z-index: 40;
        opacity: 0;
        transition: opacity 0.3s;
        text-shadow: 0 0 20px currentColor, 0 0 40px currentColor;
    }
    .flash-msg.visible { opacity: 1; }

    .mode-label {
        position: absolute;
        top: 12px; left: 50%;
        transform: translateX(-50%);
        z-index: 10;
        font-size: 11px;
        font-weight: 500;
        color: rgba(255,255,255,0.4);
        background: rgba(0,0,0,0.3);
        backdrop-filter: blur(8px);
        padding: 5px 14px;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.06);
    }

    .modal-overlay {
        position: fixed; inset: 0;
        z-index: 50;
        background: rgba(0,0,0,0.6);
        backdrop-filter: blur(12px);
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 1;
        transition: opacity 0.4s;
    }
    .modal-overlay.hidden { opacity: 0; pointer-events: none; }

    .modal-card {
        background: rgba(26,26,30,0.95);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 18px;
        padding: 32px 40px;
        max-width: 480px;
        width: 90%;
        text-align: center;
    }

    .modal-logo {
        font-family: 'Dancing Script', cursive;
        font-size: 42px;
        color: #e0e0e0;
        margin-bottom: 6px;
    }

    .modal-title {
        font-size: 20px;
        font-weight: 700;
        color: #fff;
        margin-bottom: 20px;
    }

    .gesture-cards {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        margin-bottom: 24px;
    }

    .gesture-card {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        text-align: left;
    }
    .gesture-card .emoji {
        font-size: 24px;
        width: 38px; height: 38px;
        background: rgba(255,255,255,0.06);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    .gesture-card .g-name {
        font-size: 13px;
        font-weight: 600;
        color: #fff;
        margin-bottom: 1px;
    }
    .gesture-card .g-desc {
        font-size: 11px;
        color: #888;
        line-height: 1.3;
    }

    .modal-btn {
        background: rgba(255,255,255,0.9);
        color: #111;
        border: none;
        border-radius: 24px;
        padding: 12px 40px;
        font-size: 15px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        font-family: inherit;
    }
    .modal-btn:hover {
        background: #fff;
        transform: scale(1.03);
    }

    .status-bar {
        position: absolute;
        bottom: 8px; right: 8px;
        font-size: 11px;
        color: #666;
        background: rgba(0,0,0,0.3);
        padding: 4px 10px;
        border-radius: 16px;
        z-index: 10;
    }

    /* FPS counter */
    .fps-badge {
        position: absolute;
        top: 12px; right: 180px;
        z-index: 10;
        font-size: 11px;
        color: #4ade80;
        background: rgba(0,0,0,0.4);
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 600;
        font-variant-numeric: tabular-nums;
    }
</style>
</head>
<body>

<div class="container">
    <video id="webcam" autoplay playsinline muted></video>
    <canvas id="drawCanvas"></canvas>

    <div class="camera-badge">
        <span class="status-dot"></span>
        Camera ON
    </div>

    <div class="mode-label" id="modeLabel">Loading...</div>
    <div class="fps-badge" id="fpsBadge">-- fps</div>

    <div class="sidebar">
        <div class="sidebar-label">COLORS</div>
        <div class="color-grid" id="colorGrid"></div>

        <div class="sidebar-label" style="margin-top:8px">THICKNESS</div>
        <div class="neon-star" id="neonStar">✱</div>
        <div class="slider-section">
            <input type="range" min="1" max="40" value="6" class="slider" id="brushSlider">
            <div class="slider-value" id="brushValue">6px</div>
        </div>

        <div class="sidebar-label" style="margin-top:8px">GLOW</div>
        <div class="slider-section">
            <input type="range" min="0" max="1" step="0.05" value="0.6" class="slider" id="glowSlider">
            <div class="slider-value" id="glowValue">60%</div>
        </div>

        <div class="divider"></div>

        <div class="icon-row">
            <button class="icon-btn" onclick="doUndo()" title="Undo (Z)">↩</button>
            <button class="icon-btn" onclick="doRedo()" title="Redo (Y)">↪</button>
            <button class="icon-btn" id="eraserBtn" onclick="toggleEraser()" title="Eraser (E)">⊘</button>
            <button class="icon-btn" onclick="doClear()" title="Clear (C)">🗑</button>
            <button class="icon-btn" onclick="doSave()" title="Save (S)">💾</button>
        </div>
    </div>

    <div class="bottom-bar">
        <button class="bottom-btn" onclick="toggleHand()">👋 <span id="handLabel">SHOW HAND</span></button>
    </div>

    <div class="flash-msg" id="flashMsg"></div>
    <div class="status-bar" id="status">Loading hand detection...</div>

    <div class="modal-overlay" id="modal">
        <div class="modal-card">
            <div class="modal-logo">Air Draw</div>
            <div class="modal-title">How to Play</div>
            <div class="gesture-cards">
                <div class="gesture-card">
                    <div class="emoji">☝️</div>
                    <div><div class="g-name">Draw</div><div class="g-desc">Point index finger only</div></div>
                </div>
                <div class="gesture-card">
                    <div class="emoji">✋</div>
                    <div><div class="g-name">Stop</div><div class="g-desc">Open hand to pause</div></div>
                </div>
                <div class="gesture-card">
                    <div class="emoji">✌️</div>
                    <div><div class="g-name">Idle</div><div class="g-desc">Two fingers to rest</div></div>
                </div>
                <div class="gesture-card">
                    <div class="emoji">✊</div>
                    <div><div class="g-name">Fist</div><div class="g-desc">Fist to pause drawing</div></div>
                </div>
            </div>
            <button class="modal-btn" onclick="closeModal()">Let's Go!</button>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.18/vision_bundle.mjs" type="module"></script>
<script type="module">
import { HandLandmarker, FilesetResolver } from
    "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.18/vision_bundle.mjs";

// ─── CONFIG ───
const COLORS = [
    { name:'Cyan',    hex:'#00f5ff', g:'0,245,255'   },
    { name:'Green',   hex:'#22ff44', g:'34,255,68'    },
    { name:'Magenta', hex:'#ff22cc', g:'255,34,204'   },
    { name:'Blue',    hex:'#4488ff', g:'68,136,255'   },
    { name:'Lime',    hex:'#aaff00', g:'170,255,0'    },
    { name:'Pink',    hex:'#ff4488', g:'255,68,136'   },
    { name:'Yellow',  hex:'#ffdd00', g:'255,221,0'    },
    { name:'Purple',  hex:'#bb44ff', g:'187,68,255'   },
    { name:'White',   hex:'#ffffff', g:'255,255,255'  },
    { name:'Slate',   hex:'#667788', g:'102,119,136'  },
];

let colorIdx = 0, brushSize = 6, glowAmount = 0.6;
let drawing = false, eraser = false;
let lx = 0, ly = 0;           // last raw
let sx = 0, sy = 0;           // smoothed
const ALPHA = 0.5;            // EMA factor (higher = more responsive)
let undoStack = [], redoStack = [];
let detector = null;
let showHand = true;

const canvas = document.getElementById('drawCanvas');
const ctx    = canvas.getContext('2d');
const video  = document.getElementById('webcam');

// ─── CANVAS SETUP ───
function resize() {
    canvas.width  = window.innerWidth;
    canvas.height = window.innerHeight;
}
resize();
window.addEventListener('resize', resize);

// ─── PALETTE ───
function buildPalette() {
    const grid = document.getElementById('colorGrid');
    COLORS.forEach((c, i) => {
        const d = document.createElement('button');
        d.className = 'color-dot' + (i===0?' active':'');
        d.style.background = c.hex;
        d.style.boxShadow = '0 0 8px rgba('+c.g+',0.4)';
        d.onclick = () => pickColor(i);
        grid.appendChild(d);
    });
}

function pickColor(i) {
    colorIdx = i;
    eraser = false;
    document.getElementById('eraserBtn').classList.remove('active-tool');
    document.querySelectorAll('.color-dot').forEach((d,j) => d.classList.toggle('active', j===i));
    updateStar();
    flash(COLORS[i].name, COLORS[i].hex);
}

function updateStar() {
    const s = document.getElementById('neonStar');
    s.style.color = COLORS[colorIdx].hex;
    s.style.filter = 'drop-shadow(0 0 8px rgba('+COLORS[colorIdx].g+',0.7))';
}

// ─── DRAW ───
function drawLine(x1, y1, x2, y2) {
    if (eraser) {
        ctx.save();
        ctx.globalCompositeOperation = 'destination-out';
        ctx.shadowBlur = 0;
        ctx.strokeStyle = 'rgba(0,0,0,1)';
        ctx.lineWidth = brushSize * 3;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(x1,y1); ctx.lineTo(x2,y2);
        ctx.stroke();
        ctx.restore();
        return;
    }
    const c = COLORS[colorIdx];
    ctx.save();
    if (glowAmount > 0.05) {
        ctx.shadowColor = c.hex;
        ctx.shadowBlur = 8 + glowAmount*20;
        ctx.strokeStyle = 'rgba('+c.g+','+(0.3+glowAmount*0.3)+')';
        ctx.lineWidth = brushSize * 2;
        ctx.lineCap = 'round';
        ctx.globalAlpha = 0.4;
        ctx.beginPath();
        ctx.moveTo(x1,y1); ctx.lineTo(x2,y2);
        ctx.stroke();
    }
    ctx.shadowColor = c.hex;
    ctx.shadowBlur = 3 + glowAmount*8;
    ctx.strokeStyle = c.hex;
    ctx.lineWidth = brushSize;
    ctx.lineCap = 'round';
    ctx.globalAlpha = 1;
    ctx.beginPath();
    ctx.moveTo(x1,y1); ctx.lineTo(x2,y2);
    ctx.stroke();
    ctx.restore();
}

// ─── UNDO / REDO (offscreen canvas clone) ───
function cloneCanvas() {
    const c2 = document.createElement('canvas');
    c2.width = canvas.width; c2.height = canvas.height;
    c2.getContext('2d').drawImage(canvas, 0, 0);
    return c2;
}

function pushUndo() {
    undoStack.push(cloneCanvas());
    if (undoStack.length > 20) undoStack.shift();
    redoStack = [];
}

window.doUndo = function() {
    if (undoStack.length <= 1) return;
    redoStack.push(undoStack.pop());
    ctx.clearRect(0,0,canvas.width,canvas.height);
    ctx.drawImage(undoStack[undoStack.length-1], 0, 0);
    flash('Undo','#7bd');
};

window.doRedo = function() {
    if (!redoStack.length) return;
    const s = redoStack.pop();
    undoStack.push(s);
    ctx.clearRect(0,0,canvas.width,canvas.height);
    ctx.drawImage(s, 0, 0);
    flash('Redo','#7db');
};

window.doClear = function() {
    pushUndo();
    ctx.clearRect(0,0,canvas.width,canvas.height);
    flash('Cleared','#ff5566');
};

window.doSave = function() {
    const a = document.createElement('a');
    a.download = 'air-drawing_'+Date.now()+'.png';
    a.href = canvas.toDataURL();
    a.click();
    flash('Saved!','#4ade80');
};

window.toggleEraser = function() {
    eraser = !eraser;
    document.getElementById('eraserBtn').classList.toggle('active-tool', eraser);
    flash(eraser?'Eraser ON':'Eraser OFF', eraser?'#ff6666':'#4ade80');
};

window.toggleHand = function() {
    showHand = !showHand;
    document.getElementById('handLabel').textContent = showHand?'SHOW HAND':'HIDE HAND';
};

window.closeModal = function() {
    document.getElementById('modal').classList.add('hidden');
};

let flashTimer;
function flash(text, color) {
    const el = document.getElementById('flashMsg');
    el.textContent = text;
    el.style.color = color;
    el.classList.add('visible');
    clearTimeout(flashTimer);
    flashTimer = setTimeout(() => el.classList.remove('visible'), 900);
}

// ─── SLIDERS ───
document.getElementById('brushSlider').addEventListener('input', e => {
    brushSize = +e.target.value;
    document.getElementById('brushValue').textContent = brushSize+'px';
});
document.getElementById('glowSlider').addEventListener('input', e => {
    glowAmount = +e.target.value;
    document.getElementById('glowValue').textContent = Math.round(glowAmount*100)+'%';
});

// ─── KEYBOARD ───
document.addEventListener('keydown', e => {
    const k = e.key.toLowerCase();
    if (k>='1' && k<='9' && +k<=COLORS.length) pickColor(+k-1);
    if (k==='+' || k==='=') brushSize = Math.min(brushSize+2,40);
    if (k==='-') brushSize = Math.max(brushSize-2,1);
    if (k==='z') doUndo();
    if (k==='y') doRedo();
    if (k==='c') doClear();
    if (k==='s') { e.preventDefault(); doSave(); }
    if (k==='e') toggleEraser();
});

// ─── FINGER HELPERS ───
function fingerUp(lm, tip, pip) { return lm[tip].y < lm[pip].y; }

// ─── FPS COUNTER ───
let fpsFrames = 0, fpsLast = performance.now();
function tickFps() {
    fpsFrames++;
    const now = performance.now();
    if (now - fpsLast >= 1000) {
        document.getElementById('fpsBadge').textContent = fpsFrames + ' fps';
        fpsFrames = 0;
        fpsLast = now;
    }
}

// ─── INIT ───
async function init() {
    document.getElementById('status').textContent = 'Loading AI model...';
    document.getElementById('modeLabel').textContent = 'Loading...';

    const vision = await FilesetResolver.forVisionTasks(
        'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.18/wasm'
    );

    detector = await HandLandmarker.createFromOptions(vision, {
        baseOptions: {
            modelAssetPath: 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task',
            delegate: 'GPU'
        },
        numHands: 1,
        minHandDetectionConfidence: 0.65,
        minTrackingConfidence: 0.55,
        runningMode: 'VIDEO'
    });

    document.getElementById('status').textContent = 'Starting camera...';

    // Camera — try HD first, fallback to 720p
    let stream;
    try {
        stream = await navigator.mediaDevices.getUserMedia({
            video: { width:{ideal:1920}, height:{ideal:1080}, frameRate:{ideal:30}, facingMode:'user' },
            audio: false
        });
    } catch {
        stream = await navigator.mediaDevices.getUserMedia({
            video: { width:1280, height:720, facingMode:'user' },
            audio: false
        });
    }

    video.srcObject = stream;
    const trk = stream.getVideoTracks()[0].getSettings();
    document.getElementById('modeLabel').textContent =
        'Live — ' + trk.width + '×' + trk.height + ' @ ' + Math.round(trk.frameRate||30) + 'fps';

    video.onloadedmetadata = () => {
        document.getElementById('status').style.display = 'none';
        pushUndo();
        detect();
    };
}

// ─── DETECTION LOOP ───
function detect() {
    if (!video.videoWidth || !detector) {
        requestAnimationFrame(detect);
        return;
    }

    tickFps();
    const res = detector.detectForVideo(video, performance.now());

    if (res.landmarks && res.landmarks.length > 0) {
        const lm = res.landmarks[0];

        // Mirror X for selfie view
        const rx = (1 - lm[8].x) * canvas.width;
        const ry = lm[8].y * canvas.height;

        // Smooth
        if (lx===0 && ly===0) { sx=rx; sy=ry; }
        else { sx += ALPHA*(rx-sx); sy += ALPHA*(ry-sy); }

        const idxUp = fingerUp(lm,8,6);
        const midUp = fingerUp(lm,12,10);
        const rngUp = fingerUp(lm,16,14);
        const pnkUp = fingerUp(lm,20,18);

        // Draw = only index up
        const wantDraw = idxUp && !midUp && !rngUp && !pnkUp;

        if (wantDraw) {
            if (!drawing) {
                pushUndo();
                drawing = true;
                lx = sx; ly = sy;
            }
            const d = Math.hypot(sx-lx, sy-ly);
            if (d > 1.5) {
                drawLine(lx, ly, sx, sy);
                lx = sx; ly = sy;
            }
        } else {
            drawing = false;
            lx = ly = 0;
        }
    } else {
        drawing = false;
        lx = ly = 0;
    }

    requestAnimationFrame(detect);
}

buildPalette();
updateStar();
init().catch(err => {
    document.getElementById('status').textContent = 'Error: ' + err.message;
    console.error(err);
});
</script>

</body>
</html>
"""

# Render the full app as an embedded HTML component
# height=900 gives a good fullscreen feel
st.components.v1.html(AIR_DRAW_HTML, height=900, scrolling=False)
