# Air Drawing Simulator — Vercel Deployment Edition

Draw in the air using hand gestures detected by your webcam. No mouse, no stylus — just your hand.

Built with **React/Next.js** (frontend), **Python/Flask** (backend), and **MediaPipe** (hand tracking).

![React](https://img.shields.io/badge/React-18.2-blue?logo=react)
![Next.js](https://img.shields.io/badge/Next.js-14.0-black?logo=nextjs)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10-orange)
![Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-black?logo=vercel)

---

## 🚀 Quick Start (Local)

### Prerequisites
- Node.js 16+ ([download](https://nodejs.org))
- Python 3.9+ ([download](https://python.org))

### Setup (2 minutes)

```bash
# Clone & install
git clone https://github.com/YOUR_USERNAME/Air-Drawing-Simulator.git
cd Air-Drawing-Simulator
npm install
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

### Run Locally

**Terminal 1 — Frontend (React)**
```bash
npm run dev
# Runs on http://localhost:3000
```

**Terminal 2 — Backend (Flask)**
```bash
python api/app.py
# Runs on http://localhost:5000
```

Open http://localhost:3000 in your browser and start drawing!

---

## 🌐 Deploy to Vercel (1 Click)

### Easy Deployment

1. Push to GitHub:
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

2. Go to [vercel.com](https://vercel.com)
3. Click "New Project"
4. Import your GitHub repo
5. Click "Deploy" ✨

That's it! Your app is live on `https://your-project-name.vercel.app`

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed steps.

---

## ✨ Features

✅ **Real-time Hand Detection** — MediaPipe hand tracking at 30+ FPS
✅ **Neon Glow Drawing** — Glowing strokes with customizable intensity
✅ **Dark Glassmorphism UI** — Modern frosted glass design
✅ **10 Color Palette** — Cyan, Green, Magenta, Blue, Lime, Pink, Yellow, Purple, White, Slate
✅ **Undo/Redo Stack** — Full drawing history (20 steps)
✅ **Gesture Controls** — Draw, erase, move, undo, redo, clear, save
✅ **Export Drawing** — Save as PNG with one click
✅ **Responsive Canvas** — Works on desktop and tablet (webcam required)
✅ **Mobile-Ready** — Fully responsive design

---

## 🎮 Gestures

| Gesture | Fingers | Action |
|---|---|---|
| **Index Finger** | ☝️ | Draw on canvas |
| **Open Palm** | ✋ | Erase strokes |
| **Pinch** | 🤏 | Drag & move canvas |
| **V Sign** | ✌️ | Draw rectangle |
| **3 Fingers** | 🖖 | Draw circle |
| **Thumb + Pinky** | 🤙 | Cycle colour |
| **Thumb + Middle** | | Undo |
| **Thumb + Ring** | | Redo |
| **Fist (hold 1.5s)** | ✊ | Clear canvas |
| **Rock Sign** | 🤟 | Save drawing |

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|---|---|
| `1–8` | Switch colour |
| `+` / `−` | Increase / decrease brush |
| `C` | Clear canvas |
| `S` | Save drawing |
| `Z` / `Y` | Undo / Redo |
| `E` | Toggle eraser |

---

## 📁 Project Structure

```
Air-Drawing-Simulator/
├── pages/
│   └── index.jsx              # Main React page
├── components/
│   ├── Canvas.jsx             # Drawing canvas
│   ├── Sidebar.jsx            # Controls & settings
│   ├── Modal.jsx              # Onboarding modal
│   └── FlashMessage.jsx       # Notifications
├── styles/
│   ├── globals.css            # Global dark theme
│   ├── Home.module.css        # Page layout
│   ├── Canvas.module.css      # Canvas styles
│   ├── Sidebar.module.css     # Sidebar styles
│   └── ...
├── api/
│   └── app.py                 # Flask backend (REST API)
├── package.json               # Node dependencies
├── requirements.txt           # Python dependencies
├── next.config.js             # Next.js config
├── vercel.json                # Vercel deployment config
└── README.md                  # This file
```

See [FOLDER_STRUCTURE.md](./FOLDER_STRUCTURE.md) for detailed breakdown.

---

## 🔧 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check |
| `/api/detect-hand` | POST | Detect hand gesture from image |
| `/api/canvas/init` | POST | Initialize canvas session |
| `/api/canvas/clear` | POST | Clear canvas |
| `/api/canvas/save` | POST | Export drawing as PNG |
| `/api/canvas/undo` | POST | Undo last stroke |
| `/api/canvas/redo` | POST | Redo last stroke |

---

## 🏗️ How It Works

### 1. Hand Tracking
MediaPipe detects **21 hand landmarks** in real time:
- Wrist (1)
- Thumb (4)
- Index finger (4)
- Middle finger (4)
- Ring finger (4)
- Pinky finger (4)

### 2. Gesture Recognition
Finger positions are analyzed to detect:
- Extended vs. bent fingers (by comparing tip y-coordinate to joint y-coordinate)
- Pinch distance (Euclidean distance between thumb and index tips)
- Hand orientation (left vs. right, adjusted for webcam mirroring)

### 3. Drawing
- **Smoothing**: Exponential moving average filter (α=0.55) reduces jitter
- **Neon Glow**: Outer glow layer + bright core stroke using alpha blending
- **Compositing**: Canvas overlays on webcam feed (black pixels = transparent)

### 4. Undo/Redo
- PNG-compressed snapshots stored in deques (max 20 steps)
- Snapshots taken at stroke boundaries, not per-frame
- Memory efficient while maintaining fine-grained history

---

## 🛠️ Tech Stack

### Frontend
- **React 18** — UI components
- **Next.js 14** — React framework & routing
- **CSS Modules** — Scoped component styling
- **Axios** — HTTP client for API calls

### Backend
- **Flask 3** — REST API server
- **MediaPipe** — Hand detection & landmarks
- **OpenCV** — Image processing
- **NumPy** — Numerical operations

### Deployment
- **Vercel** — Serverless hosting (frontend + backend)
- **Python 3.11** — Vercel serverless runtime

---

## 📚 Documentation

- [SETUP.md](./SETUP.md) — Quick start guide
- [DEPLOYMENT.md](./DEPLOYMENT.md) — Detailed Vercel deployment
- [FOLDER_STRUCTURE.md](./FOLDER_STRUCTURE.md) — Project file breakdown

---

## 🐛 Troubleshooting

**Webcam not working?**
- Check browser permissions (Settings → Camera)
- Ensure no other app is using the webcam
- Try refreshing the page

**Slow performance?**
- Reduce video resolution in `Canvas.jsx`
- Close unnecessary browser tabs
- Check GPU acceleration (DevTools → Performance)

**Hand not detected?**
- Ensure good lighting
- Keep hand fully visible in frame
- Try getting closer to camera

**Build fails on Vercel?**
- Check `vercel.json` is in root directory
- Verify `package.json` build script: `"build": "next build"`
- Ensure Python requirements are listed in `requirements.txt`

See [DEPLOYMENT.md](./DEPLOYMENT.md) for more troubleshooting.

---

## 🚀 Next Steps

- Add cloud storage (Firebase/S3) for drawing exports
- Implement user accounts & drawing history
- Add social sharing features
- Integrate Gemini API for AI analysis of drawings
- Create mobile app wrapper (React Native)
- Deploy backend to Cloud Run for better scalability

---

## 📄 License

MIT — Open source & free to use

---

## 🤝 Contributing

Issues and pull requests are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 👨‍💻 Built With

- Hand tracking by [MediaPipe](https://mediapipe.dev)
- UI inspired by [air-draw-one.vercel.app](https://air-draw-one.vercel.app)
- Deployed with ❤️ on [Vercel](https://vercel.com)

---

**Ready to draw?** 🎨
Start with `npm run dev` and `python api/app.py`, then open http://localhost:3000!

Questions? Check out [DEPLOYMENT.md](./DEPLOYMENT.md) or open an issue on GitHub.

**Happy drawing! 🖌️**
