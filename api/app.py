"""
Flask API backend for Air Drawing Simulator
Exposes hand tracking and drawing logic as REST endpoints
"""

import io
import cv2
import numpy as np
import mediapipe as mp
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import base64
from datetime import datetime

app = Flask(__name__)
CORS(app)

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.70,
)

# Drawing config
PINCH_THRESHOLD = 0.055
MAX_UNDO_STEPS = 20

# Canvas storage (in-memory, resets per session)
canvas_buffer = {}


# ═══════════════════════════════════════════════════
#  HEALTH CHECK
# ═══════════════════════════════════════════════════

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Air Draw API is running'}), 200


# ═══════════════════════════════════════════════════
#  HAND DETECTION
# ═══════════════════════════════════════════════════

def fingers_up(hand_landmarks, handedness="Right"):
    """Return [thumb, index, middle, ring, pinky] booleans."""
    lm = hand_landmarks.landmark
    tips = [4, 8, 12, 16, 20]
    joints = [3, 6, 10, 14, 18]
    result = []
    if handedness == "Right":
        result.append(lm[4].x < lm[3].x)
    else:
        result.append(lm[4].x > lm[3].x)
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
        return "rect"
    return "idle"


@app.route('/api/detect-hand', methods=['POST'])
def detect_hand():
    """
    Detect hand in a frame and return gesture.
    Expects: base64-encoded image in 'image' field
    Returns: gesture, hand landmarks, confidence
    """
    try:
        data = request.json
        image_b64 = data.get('image')

        if not image_b64:
            return jsonify({'error': 'No image provided'}), 400

        # Decode base64 image
        img_data = base64.b64decode(image_b64)
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        h, w = frame.shape[:2]

        # Convert to RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        gesture = "idle"
        landmarks = None
        handedness_label = "Right"
        confidence = 0.0

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            if results.multi_handedness:
                handedness_label = results.multi_handedness[0].classification[0].label
                confidence = results.multi_handedness[0].classification[0].score

            gesture = detect_gesture(hand, handedness_label)

            # Extract index fingertip
            index_lm = hand.landmark[8]
            landmarks = {
                'index_x': index_lm.x,
                'index_y': index_lm.y,
                'index_z': index_lm.z,
            }

            # Extract all 21 landmarks
            all_landmarks = []
            for lm in hand.landmark:
                all_landmarks.append({'x': lm.x, 'y': lm.y, 'z': lm.z})

            landmarks['all_landmarks'] = all_landmarks

        return jsonify({
            'gesture': gesture,
            'landmarks': landmarks,
            'handedness': handedness_label,
            'confidence': float(confidence),
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════
#  CANVAS OPERATIONS
# ═══════════════════════════════════════════════════

@app.route('/api/canvas/init', methods=['POST'])
def canvas_init():
    """Initialize a new canvas session."""
    try:
        session_id = request.json.get('session_id', 'default')
        width = request.json.get('width', 1280)
        height = request.json.get('height', 720)

        canvas_buffer[session_id] = {
            'image': np.zeros((height, width, 3), dtype=np.uint8),
            'undo_stack': [],
            'redo_stack': [],
        }

        return jsonify({
            'session_id': session_id,
            'width': width,
            'height': height,
            'status': 'initialized',
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/canvas/clear', methods=['POST'])
def canvas_clear():
    """Clear the canvas."""
    try:
        session_id = request.json.get('session_id', 'default')

        if session_id not in canvas_buffer:
            return jsonify({'error': 'Canvas not initialized'}), 400

        canvas_buffer[session_id]['image'] = np.zeros_like(canvas_buffer[session_id]['image'])

        return jsonify({'status': 'cleared'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/canvas/save', methods=['POST'])
def canvas_save():
    """Save canvas as PNG and return base64-encoded image."""
    try:
        session_id = request.json.get('session_id', 'default')

        if session_id not in canvas_buffer:
            return jsonify({'error': 'Canvas not initialized'}), 400

        canvas_img = canvas_buffer[session_id]['image']

        # Encode to PNG
        _, buffer = cv2.imencode('.png', canvas_img)
        img_b64 = base64.b64encode(buffer).decode('utf-8')

        return jsonify({
            'image': img_b64,
            'filename': f"air-drawing-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png",
            'status': 'saved',
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/canvas/undo', methods=['POST'])
def canvas_undo():
    """Undo last stroke."""
    try:
        session_id = request.json.get('session_id', 'default')

        if session_id not in canvas_buffer:
            return jsonify({'error': 'Canvas not initialized'}), 400

        if not canvas_buffer[session_id]['undo_stack']:
            return jsonify({'status': 'nothing_to_undo'}), 200

        # Move current to redo
        current = canvas_buffer[session_id]['image'].copy()
        canvas_buffer[session_id]['redo_stack'].append(current)

        # Pop from undo
        canvas_buffer[session_id]['image'] = canvas_buffer[session_id]['undo_stack'].pop()

        return jsonify({'status': 'undone'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/canvas/redo', methods=['POST'])
def canvas_redo():
    """Redo last undone stroke."""
    try:
        session_id = request.json.get('session_id', 'default')

        if session_id not in canvas_buffer:
            return jsonify({'error': 'Canvas not initialized'}), 400

        if not canvas_buffer[session_id]['redo_stack']:
            return jsonify({'status': 'nothing_to_redo'}), 200

        # Move current to undo
        current = canvas_buffer[session_id]['image'].copy()
        canvas_buffer[session_id]['undo_stack'].append(current)

        # Pop from redo
        canvas_buffer[session_id]['image'] = canvas_buffer[session_id]['redo_stack'].pop()

        return jsonify({'status': 'redone'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════
#  ERROR HANDLERS
# ═══════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
