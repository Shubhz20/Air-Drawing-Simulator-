# Quick Setup Guide

## Prerequisites

- Node.js 16+ ([download](https://nodejs.org))
- Python 3.9+ ([download](https://python.org))
- Git ([download](https://git-scm.com))
- GitHub account ([create free](https://github.com/signup))
- Vercel account ([create free](https://vercel.com/signup))

## Local Development (5 minutes)

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/Air-Drawing-Simulator.git
cd Air-Drawing-Simulator
```

### 2. Install Dependencies
```bash
# Node.js packages
npm install

# Python virtual environment
python -m venv venv

# Activate venv
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install Python packages
pip install -r requirements.txt
```

### 3. Run Development Servers

**Terminal 1 — Frontend (Next.js on port 3000)**
```bash
npm run dev
```

**Terminal 2 — Backend (Flask on port 5000)**
```bash
python api/app.py
```

### 4. Open in Browser
```
http://localhost:3000
```

## Deploy to Vercel (2 minutes)

### 1. Push to GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### 2. Deploy via Vercel CLI
```bash
npm install -g vercel
vercel
```

**Or** via [Vercel Dashboard](https://vercel.com/new):
- Click "New Project"
- Import GitHub repo
- Click "Deploy"

### 3. Access Your Live App
```
https://air-drawing-simulator.vercel.app
```

---

## Project Structure

```
📦 Air-Drawing-Simulator
├── 📁 pages/           # React pages (Next.js)
├── 📁 components/      # React components
├── 📁 styles/          # CSS modules
├── 📁 api/             # Python Flask backend
├── 📁 public/          # Static assets
├── 📄 package.json     # Node dependencies
├── 📄 requirements.txt # Python dependencies
├── 📄 vercel.json      # Vercel config
└── 📄 README.md        # Documentation
```

---

## Features

✅ Real-time hand gesture tracking
✅ Neon glow drawing effects
✅ Undo/redo functionality
✅ 10-color palette
✅ Export as PNG
✅ Dark glassmorphic UI
✅ Mobile responsive

---

## Common Commands

| Command | What It Does |
|---------|-------------|
| `npm run dev` | Start Next.js dev server |
| `npm run build` | Build for production |
| `npm run start` | Run production build |
| `python api/app.py` | Start Flask backend |
| `vercel` | Deploy to Vercel |
| `git push` | Push changes to GitHub |

---

## Troubleshooting

**Problem:** `npm: command not found`
**Solution:** Install Node.js from https://nodejs.org

**Problem:** `ModuleNotFoundError: No module named 'flask'`
**Solution:** Run `pip install -r requirements.txt` in activated venv

**Problem:** Port 3000 or 5000 already in use
**Solution:** Kill the process or use different ports:
```bash
npm run dev -- -p 3001
python api/app.py --port 5001
```

**Problem:** Webcam not working
**Solution:**
- Allow webcam permission in browser
- Check if other apps are using webcam
- Try a different browser

---

## Next: Full Deployment Guide

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed Vercel deployment steps.

---

**Questions?** Open an issue on GitHub or check [Vercel Docs](https://vercel.com/docs)

🚀 **Happy drawing!**
