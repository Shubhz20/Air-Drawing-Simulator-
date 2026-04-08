# Complete Project Folder Structure

```
Air-Drawing-Simulator/
│
├── 📁 pages/
│   └── index.jsx                    # Main Next.js page (React app entry)
│
├── 📁 components/                   # React components
│   ├── Canvas.jsx                   # Drawing canvas with webcam integration
│   ├── Sidebar.jsx                  # Control sidebar (colors, sliders, buttons)
│   ├── Modal.jsx                    # Onboarding modal
│   └── FlashMessage.jsx             # Temporary notification display
│
├── 📁 styles/                       # CSS modules (scoped styling)
│   ├── globals.css                  # Global CSS (dark theme setup)
│   ├── Home.module.css              # Page-level styles
│   ├── Canvas.module.css            # Canvas component styles
│   ├── Sidebar.module.css           # Sidebar component styles
│   ├── Modal.module.css             # Modal component styles
│   └── FlashMessage.module.css      # Flash message styles
│
├── 📁 api/                          # Python backend (Vercel serverless)
│   └── app.py                       # Flask API with hand detection endpoints
│
├── 📁 public/                       # Static assets (optional)
│   └── favicon.ico                  # Website icon
│
├── 📄 package.json                  # NPM dependencies & scripts
├── 📄 requirements.txt              # Python dependencies for Flask backend
├── 📄 next.config.js               # Next.js configuration
├── 📄 vercel.json                  # Vercel deployment configuration
├── 📄 .gitignore                   # Git ignore rules
│
├── 📄 README.md                    # Main project documentation
├── 📄 SETUP.md                     # Quick start guide
├── 📄 DEPLOYMENT.md                # Detailed deployment instructions
└── 📄 FOLDER_STRUCTURE.md          # This file
```

## Directory Details

### `/pages`
- **index.jsx** — Main React page served by Next.js
  - Imports all components (Canvas, Sidebar, Modal, FlashMessage)
  - Manages global state (colors, brush size, glow, etc.)
  - Handles user interactions (clicks, keyboard, canvas drawing)

### `/components`
Reusable React components:
- **Canvas.jsx** — Drawing canvas with webcam video processing
  - Handles real-time drawing
  - Manages undo/redo stack
  - Exports drawing as PNG
  - Integrates with Flask hand detection API

- **Sidebar.jsx** — Right-side control panel
  - 10-color palette selector
  - Brush thickness slider (1-40px)
  - Glow effect slider (0-100%)
  - Action buttons (Undo, Clear, Eraser, Save)

- **Modal.jsx** — Onboarding modal
  - Displays on first load
  - Shows gesture guide (Draw, Erase, Move, Idle)
  - "Let's Go!" button to start

- **FlashMessage.jsx** — Toast notifications
  - Shows temporary feedback (1 second duration)
  - Neon glow effects
  - Color-coded messages

### `/styles`
CSS modules for component styling:
- **globals.css** — Global dark theme, font imports, resets
- **Home.module.css** — Page layout (camera badge, mode label, bottom toggle)
- **Canvas.module.css** — Canvas positioning and rendering
- **Sidebar.module.css** — Sidebar panel, sliders, color grid, buttons
- **Modal.module.css** — Modal card, animations, gesture cards
- **FlashMessage.module.css** — Flash notification styling and animations

### `/api`
Python backend (Flask):
- **app.py** — REST API with endpoints:
  - `GET /api/health` — Health check
  - `POST /api/detect-hand` — Hand gesture detection (MediaPipe)
  - `POST /api/canvas/init` — Initialize canvas session
  - `POST /api/canvas/clear` — Clear canvas
  - `POST /api/canvas/save` — Export drawing as PNG
  - `POST /api/canvas/undo` — Undo last stroke
  - `POST /api/canvas/redo` — Redo stroke
  - CORS enabled for frontend integration

### `/public`
Static files served by Next.js:
- Optional favicon, images, or other static assets

### Root Configuration Files

- **package.json** — Node.js dependencies
  ```json
  {
    "scripts": {
      "dev": "next dev",          // Local dev (port 3000)
      "build": "next build",      // Production build
      "start": "next start"       // Run built app
    },
    "dependencies": {
      "react": "^18.2.0",
      "next": "^14.0.0",
      "axios": "^1.6.0"
    }
  }
  ```

- **requirements.txt** — Python packages
  ```
  flask==3.0.0
  flask-cors==4.0.0
  opencv-python-headless==4.9.0.80
  mediapipe==0.10.9
  numpy==1.26.4
  ```

- **next.config.js** — Next.js build configuration
  - React strict mode enabled
  - SWC minification enabled

- **vercel.json** — Vercel deployment config
  ```json
  {
    "buildCommand": "npm run build",
    "framework": "nextjs",
    "functions": {
      "api/app.py": {
        "runtime": "python3.11"
      }
    }
  }
  ```

- **.gitignore** — Git ignore patterns
  - Excludes: node_modules/, venv/, __pycache__/, .env, .next/, build/

## Data Flow

```
User Browser
    ↓
┌─────────────────┐
│ React Frontend  │ (pages/index.jsx + components/)
│                 │
│ - Canvas draws  │
│ - UI controls   │
│ - Sidebar panel │
└────────┬────────┘
         ↓
    API Call
  (axios/fetch)
         ↓
┌─────────────────────────────┐
│  Flask Backend (api/app.py) │
│                             │
│ - Hand detection            │
│ - Canvas operations         │
│ - Undo/Redo logic           │
│ - PNG export                │
└────────┬────────────────────┘
         ↓
Response (JSON/Base64)
         ↓
   React Updates
   & Display
```

## File Sizes (Estimated)

| File | Purpose | Size |
|------|---------|------|
| pages/index.jsx | Main page | ~3 KB |
| components/*.jsx | Components | ~5 KB total |
| styles/*.css | Styling | ~4 KB total |
| api/app.py | Backend | ~6 KB |
| Configuration files | Configs | ~2 KB total |

**Total Project Size**: ~20 KB (before dependencies)

## Deployment Paths

### Local Development
```
localhost:3000  ← Next.js frontend
     ↓
localhost:5000  ← Flask API
```

### Vercel Production
```
https://air-drawing-simulator.vercel.app          ← Next.js
         ↓
https://air-drawing-simulator.vercel.app/api/... ← Flask serverless
```

## How to Navigate

1. **Start Development**: Read `SETUP.md`
2. **Understand Code**: Start with `pages/index.jsx`
3. **Deploy to Production**: Follow `DEPLOYMENT.md`
4. **Modify UI**: Edit `components/*.jsx` and `styles/*.module.css`
5. **Modify Logic**: Edit `api/app.py` (Python) or `pages/index.jsx` (React)
6. **Add Features**: Create new components in `/components`

---

**Next**: Run `npm install && python -m venv venv && pip install -r requirements.txt` to get started! 🚀
