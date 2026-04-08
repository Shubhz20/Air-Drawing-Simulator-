# ✅ Vercel Deployment Checklist

Complete this checklist to successfully deploy your Air Drawing Simulator to Vercel.

---

## 📋 Pre-Deployment (Local Setup)

- [ ] Clone repository to your computer
- [ ] Install Node.js 16+ ([nodejs.org](https://nodejs.org))
- [ ] Install Python 3.9+ ([python.org](https://python.org))
- [ ] Install Git ([git-scm.com](https://git-scm.com))
- [ ] Run `npm install` (install Node dependencies)
- [ ] Create Python venv: `python -m venv venv`
- [ ] Activate venv (macOS/Linux: `source venv/bin/activate` | Windows: `venv\Scripts\activate`)
- [ ] Run `pip install -r requirements.txt` (install Python dependencies)

## 🧪 Local Testing

- [ ] Start Next.js dev server: `npm run dev` (should be on http://localhost:3000)
- [ ] Start Flask backend: `python api/app.py` (should be on http://localhost:5000)
- [ ] Open http://localhost:3000 in browser
- [ ] Test drawing with mouse (simulates hand gestures)
- [ ] Test color switching (click colors or press 1-8)
- [ ] Test brush size slider (should adjust drawing thickness)
- [ ] Test glow slider (should affect neon glow effect)
- [ ] Test undo button (↩)
- [ ] Test clear button (🗑)
- [ ] Test eraser button (⊘)
- [ ] Test save button (💾) — should download PNG
- [ ] Test modal opens on first load — click "Let's Go!"
- [ ] Test bottom toggle (Show/Hide Hand)

## 📤 GitHub Preparation

- [ ] Create GitHub account ([github.com/signup](https://github.com/signup))
- [ ] Create new repository named `Air-Drawing-Simulator`
- [ ] Initialize git in your project folder:
  ```bash
  git init
  git add .
  git commit -m "Initial commit: Air Drawing Simulator"
  git remote add origin https://github.com/YOUR_USERNAME/Air-Drawing-Simulator.git
  git branch -M main
  git push -u origin main
  ```
- [ ] Verify all files are on GitHub:
  - [ ] `package.json` ✓
  - [ ] `requirements.txt` ✓
  - [ ] `vercel.json` ✓
  - [ ] `api/app.py` ✓
  - [ ] `pages/index.jsx` ✓
  - [ ] `components/*.jsx` ✓
  - [ ] `styles/*.css` ✓

## 🌐 Vercel Setup

- [ ] Create Vercel account ([vercel.com/signup](https://vercel.com/signup))
- [ ] Sign in with GitHub account
- [ ] Go to [vercel.com/new](https://vercel.com/new)
- [ ] Click "Import Project"
- [ ] Select your `Air-Drawing-Simulator` GitHub repository
- [ ] Verify project settings:
  - [ ] Framework: **Next.js** (should auto-detect)
  - [ ] Build Command: `npm run build` (should auto-fill)
  - [ ] Output Directory: `.next` (should auto-fill)
  - [ ] Root Directory: `./` (default)
- [ ] Add Environment Variables (optional):
  - [ ] `NEXT_PUBLIC_API_URL`: Leave blank (Vercel auto-detects)
- [ ] Click **"Deploy"** button

## ⏳ Deployment Progress

- [ ] Vercel starts building (takes 1-3 minutes)
- [ ] Build logs show:
  - [ ] `> npm run build` ✓
  - [ ] Next.js compilation successful ✓
  - [ ] Python dependencies installed ✓
- [ ] Build completes without errors
- [ ] Deployment successful message appears
- [ ] Live URL provided (e.g., `https://air-drawing-simulator.vercel.app`)

## 🧪 Post-Deployment Testing

- [ ] Open live URL in browser (https://your-project.vercel.app)
- [ ] Wait for page to load (may take 5-10 seconds on first load)
- [ ] Test all features:
  - [ ] Webcam permission dialog appears
  - [ ] Modal displays "How to Play" on first visit
  - [ ] Drawing works (if webcam available) OR mouse simulation works
  - [ ] Colors can be selected
  - [ ] Brush size slider works
  - [ ] Glow slider works
  - [ ] Undo/Clear/Eraser/Save buttons work
  - [ ] Drawing exports as PNG
  - [ ] No console errors (F12 → Console tab)

## 🔧 Troubleshooting

### Build Failed?

- [ ] Check vercel.json is in root directory
- [ ] Verify package.json has correct build script
- [ ] Check requirements.txt has all Python packages
- [ ] Review build logs for specific errors
- [ ] Try redeploying: Go to Vercel → Project → Redeploy

### App Works Locally but Not on Vercel?

- [ ] Check browser console for JavaScript errors (F12)
- [ ] Check Network tab to see failed API calls
- [ ] Verify `NEXT_PUBLIC_API_URL` environment variable
- [ ] Ensure Flask backend is accessible from frontend
- [ ] Try clearing browser cache (Ctrl+Shift+Delete)

### Webcam Not Working?

- [ ] Grant permission when prompted
- [ ] Some browsers require HTTPS (Vercel provides this ✓)
- [ ] Try different browser (Chrome recommended)
- [ ] Check if another tab has webcam access

### API Calls Failing?

- [ ] Verify `/api/app.py` exists
- [ ] Check `vercel.json` has correct function configuration
- [ ] Ensure CORS is enabled in Flask (it is by default ✓)
- [ ] Test API directly: https://your-project.vercel.app/api/health
  - Should return: `{"status":"ok","message":"Air Draw API is running"}`

## 🎉 Success Indicators

Your deployment is successful when:

✅ Live URL works in browser
✅ No build errors or warnings
✅ All UI elements display correctly
✅ Drawing/Canvas functional
✅ API endpoints respond (test /api/health)
✅ No console errors (F12)
✅ App loads within 5 seconds
✅ Mobile-responsive design works

## 📊 Performance Metrics (Vercel Dashboard)

After deployment, check in Vercel Dashboard:

- [ ] **Builds**: Latest build successful
- [ ] **Deployments**: Latest deployment is Production
- [ ] **Domains**: Custom domain (if applicable)
- [ ] **Analytics**: Page loads showing
- [ ] **Logs**: No error logs in Recent Activity

## 🚀 Next Steps (Optional)

- [ ] **Custom Domain**: Add your own domain (Vercel Dashboard → Settings)
- [ ] **Analytics**: Enable Vercel Analytics (free)
- [ ] **CI/CD**: Set up automatic deployments on git push (auto-enabled ✓)
- [ ] **Monitoring**: Set up email alerts for deploy failures
- [ ] **Firewall**: Enable security headers (optional)

## 📞 Need Help?

If something goes wrong:

1. **Check Logs**: Vercel Dashboard → Project → Deployments → Logs
2. **Read Docs**: [DEPLOYMENT.md](./DEPLOYMENT.md) in this repo
3. **Vercel Help**: [vercel.com/docs](https://vercel.com/docs)
4. **GitHub Issue**: Create issue in your repository
5. **Stack Overflow**: Search "Next.js Flask deployment"

---

## Summary

**Total Time to Deploy**: ~15 minutes (5 min setup + 3 min build + 2 min testing)

**Cost**: FREE (Vercel & GitHub free tier)

**Live After**: Click deploy → wait 3 minutes → your app is live!

---

**Congratulations on deploying your Air Drawing Simulator! 🎉**

Now share your live URL and let people draw from anywhere in the world! 🎨

---

For detailed instructions, see:
- [SETUP.md](./SETUP.md) — Quick start
- [DEPLOYMENT.md](./DEPLOYMENT.md) — Full deployment guide
- [FOLDER_STRUCTURE.md](./FOLDER_STRUCTURE.md) — Project overview
- [README.md](./README.md) — Features & how it works
