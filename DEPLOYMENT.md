# Air Drawing Simulator — Vercel Deployment Guide

## Project Structure

```
Air-Drawing-Simulator/
├── pages/
│   └── index.jsx                 # Main React page
├── components/
│   ├── Canvas.jsx                # Canvas drawing component
│   ├── Sidebar.jsx               # Sidebar with controls
│   ├── Modal.jsx                 # Onboarding modal
│   └── FlashMessage.jsx          # Flash notification
├── styles/
│   ├── globals.css               # Global styles
│   ├── Home.module.css           # Page styles
│   ├── Canvas.module.css         # Canvas styles
│   ├── Sidebar.module.css        # Sidebar styles
│   ├── Modal.module.css          # Modal styles
│   └── FlashMessage.module.css   # Flash styles
├── api/
│   └── app.py                    # Flask API backend
├── public/
│   └── favicon.ico               # Optional favicon
├── package.json                  # NPM dependencies
├── requirements.txt              # Python dependencies
├── next.config.js                # Next.js config
├── vercel.json                   # Vercel deployment config
└── README.md                     # Documentation
```

## Step-by-Step Deployment Guide

### Step 1: Prepare Your Local Environment

```bash
# Navigate to project directory
cd Air-Drawing-Simulator

# Install Node.js dependencies
npm install

# Install Python dependencies (optional, for local testing)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Test Locally

```bash
# Terminal 1: Run Next.js frontend (port 3000)
npm run dev

# Terminal 2: Run Flask API (port 5000)
python api/app.py

# Visit: http://localhost:3000
```

### Step 3: Push to GitHub

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit: Air Drawing Simulator"
git remote add origin https://github.com/YOUR_USERNAME/Air-Drawing-Simulator.git
git branch -M main
git push -u origin main
```

### Step 4: Deploy to Vercel

#### Option A: Via Vercel Dashboard

1. Go to [vercel.com](https://vercel.com)
2. Sign in with GitHub
3. Click "New Project"
4. Select your `Air-Drawing-Simulator` repository
5. Framework preset: Select "Next.js"
6. Environment variables:
   - `NEXT_PUBLIC_API_URL`: Leave as default (Vercel will auto-set)
7. Click "Deploy"

#### Option B: Via Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Follow prompts:
# - Link to existing project or create new
# - Set project name
# - Set build command: npm run build
# - Set output directory: .next
```

### Step 5: Verify Deployment

1. After deployment completes, you'll get a live URL (e.g., `https://air-drawing-simulator.vercel.app`)
2. Test the app:
   - Check webcam permission dialog
   - Try drawing with mouse (simulated hand)
   - Test all buttons (undo, clear, save)
   - Verify colors change
   - Check brush size slider

### Step 6: Configure Environment Variables (if needed)

In Vercel Dashboard:
1. Go to Project Settings
2. Environment Variables
3. Add:
   - `NEXT_PUBLIC_API_URL`: `https://air-drawing-simulator.vercel.app/api`

## File Descriptions

### Frontend (React/Next.js)

| File | Purpose |
|------|---------|
| `pages/index.jsx` | Main page component, manages state |
| `components/Canvas.jsx` | Drawing canvas with WebGL rendering |
| `components/Sidebar.jsx` | Color picker, brush size, controls |
| `components/Modal.jsx` | Onboarding "How to Play" modal |
| `components/FlashMessage.jsx` | Temporary notification display |
| `styles/*.module.css` | Scoped component styles |
| `styles/globals.css` | Global dark theme CSS |

### Backend (Flask)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check |
| `/api/detect-hand` | POST | Detect hand gestures in image |
| `/api/canvas/init` | POST | Initialize canvas session |
| `/api/canvas/clear` | POST | Clear canvas |
| `/api/canvas/save` | POST | Save and export drawing |
| `/api/canvas/undo` | POST | Undo last stroke |
| `/api/canvas/redo` | POST | Redo last stroke |

### Configuration

| File | Purpose |
|------|---------|
| `package.json` | NPM scripts and dependencies |
| `requirements.txt` | Python package dependencies |
| `next.config.js` | Next.js configuration |
| `vercel.json` | Vercel deployment settings |
| `.gitignore` | Git ignore rules |

## Key Features

✅ **Real-time Hand Detection** — MediaPipe hand tracking
✅ **Neon Glow Drawing** — Glow effect on strokes
✅ **Dark Glassmorphism UI** — Modern frosted glass design
✅ **10 Color Palette** — Cyan, Green, Magenta, Blue, etc.
✅ **Undo/Redo Stack** — Full drawing history
✅ **Gesture-based Controls** — Index finger, palm, pinch, etc.
✅ **Responsive Canvas** — Works on all screen sizes
✅ **Export Drawing** — Save as PNG image

## Troubleshooting

### Issue: "No module named 'flask'"
```bash
pip install -r requirements.txt
```

### Issue: Webcam not working
- Check browser permissions
- Allow webcam access when prompted
- Try refreshing the page

### Issue: Vercel build fails
- Ensure `vercel.json` is in root directory
- Check `package.json` has correct build script
- Verify Python requirements are listed

### Issue: API calls failing
- Check `NEXT_PUBLIC_API_URL` environment variable
- Ensure Flask backend is running locally
- Check CORS headers in `api/app.py`

## API Response Examples

### Hand Detection
```json
{
  "gesture": "draw",
  "landmarks": {
    "index_x": 0.5,
    "index_y": 0.3,
    "index_z": -0.1,
    "all_landmarks": [...]
  },
  "handedness": "Right",
  "confidence": 0.95
}
```

### Save Canvas
```json
{
  "image": "iVBORw0KGgoAAAANSUhEUgA...",
  "filename": "air-drawing-20240407-120530.png",
  "status": "saved"
}
```

## Performance Tips

1. **Optimize Webcam Resolution**: Reduce if performance is slow
2. **Enable GPU Acceleration**: Use browser DevTools to check
3. **Lazy Load Components**: Use dynamic imports for heavy components
4. **Cache API Responses**: Consider caching gesture predictions
5. **Monitor Bundle Size**: Use `npm run build && npm run analyze`

## Next Steps

- Add cloud storage (Firebase/AWS S3) for drawing exports
- Implement user accounts and drawing history
- Add social sharing features
- Integrate AI analysis of drawings (Gemini API)
- Add mobile app wrapper (React Native)
- Deploy Python backend to Cloud Run for better scalability

## Support

For issues or questions:
- Check [Vercel Docs](https://vercel.com/docs)
- Review [Next.js Guide](https://nextjs.org/docs)
- See [Flask Documentation](https://flask.palletsprojects.com)

---

**Happy Drawing! 🎨**
