# Air Drawing Simulator

A high-performance, real-time hand gesture-based drawing application. This platform utilizes computer vision to translate hand movements into digital illustrations, providing a touchless drawing experience directly via the browser.

## Overview

The Air Drawing Simulator leverages MediaPipe's hand tracking capabilities and OpenCV's image processing to provide a robust drawing interface. The application is built using Streamlit and integrated with WebRTC to ensure low-latency video streaming and real-time gesture recognition.

## Professional Features

*   **Real-time Hand Landmark Detection:** Utilizes MediaPipe for precise tracking of 21 hand landmarks at high fidelity.
*   **Neon Aesthetic Engine:** Implements advanced alpha blending and glow effects for a modern, neon-themed drawing experience.
*   **Touchless Interface:** Support for various hand gestures to control drawing, erasing, and canvas management.
*   **WebRTC Integration:** Optimized for reliable webcam connectivity behind NAT and firewalls using TURN server infrastructure.
*   **State Management:** Features a built-in undo/redo stack and canvas persistence.

## Technology Stack

*   **Language:** Python 3.10+
*   **Web Framework:** Streamlit
*   **Computer Vision:** MediaPipe, OpenCV
*   **Real-time Communication:** Streamlit-WebRTC (AIOICE)
*   **Numerical Processing:** NumPy

## Installation and Local Setup

### Prerequisites

*   Python 3.10 or higher
*   Webcam access

### Configuration

1.  Clone the repository:
    ```bash
    git clone https://github.com/Shubhz20/Air-Drawing-Simulator-.git
    cd Air-Drawing-Simulator-
    ```

2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  Install required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  Configure system dependencies (Linux/Debian):
    Refer to `packages.txt` for the required apt packages, including `libgl1` and `libglib2.0-0t64`.

### Usage

Execute the following command to launch the application:

```bash
streamlit run app.py
```

Navigate to the provided local URL (typically `http://localhost:8501`) to access the interface.

## Control Gestures

| Gesture | Action |
| --- | --- |
| **Index Finger Extended** | Draw on Canvas |
| **Open Palm** | Eraser Mode |
| **Pinch (Thumb and Index)** | Transform/Move Mode |
| **Two Fingers (Index and Middle)** | Idle/Pause Mode |

## Deployment

This application is optimized for deployment on **Streamlit Community Cloud**. It includes necessary configurations for:

*   **Packages:** `packages.txt` for system-level dependencies.
*   **WebRTC:** Integrated TURN server configuration for cross-network compatibility.

## Technical Challenges and Solutions

### 1. Deployment Optimization
Initially, the project targeted Vercel's serverless architecture. However, the 250MB functional limit was exceeded by necessary machine learning dependencies (MediaPipe, OpenCV).
*   **Solution:** Migrated the deployment to Streamlit Community Cloud, which is better optimized for large-scale Python dependency management and real-time visualization.

### 2. Network Traversal (NAT/Firewall)
Real-time video streaming in cloud environments often fails due to complex network configurations (NAT/Firewalls) blocking direct peer-to-peer connections.
*   **Solution:** Integrated a dedicated TURN server relay via Metered.ca. The application dynamically fetches fresh credentials to maintain reliable webcam connectivity across diverse network environments.

### 3. MediaPipe Integration in Streamlit
Initializing MediaPipe objects within Streamlit's worker threads led to resource leaks and attribute errors.
*   **Solution:** Refactored MediaPipe initialization to a stable global scope and optimized the video processor factory to handle frames efficiently without re-initializing the model on every loop.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

*   Hand tracking powered by MediaPipe.
*   Real-time streaming enabled by the Streamlit-WebRTC project.
