# Deploy to Render - Step by Step Guide

## Prerequisites

1. GitHub account (free)
2. Render account (free tier available)
3. Your code pushed to GitHub

## Step 1: Push Code to GitHub

### If you don't have a GitHub repository yet:

1. **Create a new repository on GitHub:**
   - Go to https://github.com/new
   - Name it: `website-screenshot-api` (or any name)
   - Make it **Public** (free Render tier requires public repos)
   - Don't initialize with README
   - Click "Create repository"

2. **Push your code:**
   ```bash
   cd C:\Users\USER\cursor-tutor\API_SS
   
   # Initialize git (if not already done)
   git init
   
   # Add all files
   git add .
   
   # Commit
   git commit -m "Initial commit - Website Screenshot API"
   
   # Add GitHub remote (replace YOUR_USERNAME and REPO_NAME)
   git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
   
   # Push to GitHub
   git branch -M main
   git push -u origin main
   ```

### If you already have a GitHub repository:

```bash
cd C:\Users\USER\cursor-tutor\API_SS
git add .
git commit -m "Update for Render deployment"
git push
```

## Step 2: Create Render Account

1. Go to https://render.com
2. Sign up with GitHub (easiest way)
3. Authorize Render to access your GitHub

## Step 3: Create Web Service on Render

1. **Go to Dashboard:**
   - Click "New +" button
   - Select "Web Service"

2. **Connect Repository:**
   - Click "Connect account" if needed
   - Find and select your repository
   - Click "Connect"

3. **Configure Service:**
   - **Name:** `website-screenshot-api` (or any name)
   - **Region:** Choose closest to you (e.g., `Oregon (US West)`)
   - **Branch:** `main` (or `master`)
   - **Root Directory:** Leave empty (or `./` if your files are in root)
   - **Environment:** Select **Docker**
   - **Dockerfile Path:** `Dockerfile` (should auto-detect)
   - **Docker Context:** Leave empty
   - **Instance Type:** `Free` (or upgrade if needed)
   - **Auto-Deploy:** `Yes` (deploys on every push)

4. **Advanced Settings (Optional):**
   - Click "Advanced"
   - **Health Check Path:** Leave empty (or `/`)
   - **Start Command:** Leave empty (Dockerfile handles this)

5. **Click "Create Web Service"**

## Step 4: Wait for Deployment

- Render will:
  1. Clone your repository
  2. Build Docker image (this takes 5-10 minutes first time)
  3. Install Playwright browsers
  4. Start your service

- You'll see build logs in real-time
- First deployment takes 10-15 minutes (downloading Playwright browsers)

## Step 5: Get Your API URL

Once deployed:
- Your API will be at: `https://website-screenshot-api.onrender.com`
- Or: `https://your-service-name.onrender.com`

## Step 6: Test Your Deployed API

```powershell
# Test root endpoint
Invoke-RestMethod -Uri "https://your-app.onrender.com/"

# Test screenshot endpoint
Invoke-WebRequest -Uri "https://your-app.onrender.com/screenshot?url=https://example.com" -OutFile "test.png"
```

## Step 7: Use in n8n

In n8n HTTP Request node:
- **URL:** `https://your-app.onrender.com/screenshot?url={{$json.url}}`
- **Method:** GET
- **Response Format:** File
- **Binary Data:** true

## Important Notes

### Free Tier Limitations:
- ⚠️ **Spins down after 15 minutes of inactivity**
- First request after spin-down takes 30-60 seconds (cold start)
- Subsequent requests are fast
- 750 hours/month free

### To Keep It Awake (Optional):
- Use a cron job or monitoring service to ping it every 10 minutes
- Or upgrade to paid plan ($7/month) for always-on

### Environment Variables (if needed later):
- Go to your service → Environment
- Add variables like:
  - `PORT=8000` (usually not needed, Render auto-sets)

## Troubleshooting

### Build Fails:
- Check Dockerfile is in root directory
- Check requirements.txt exists
- Check build logs for errors

### Service Won't Start:
- Check logs in Render dashboard
- Verify Dockerfile CMD is correct
- Check port is 8000

### Slow First Request:
- Normal on free tier (cold start)
- Service spins up automatically

### Playwright Not Working:
- Check Dockerfile installs browsers correctly
- Check build logs for Playwright installation

## Quick Checklist

- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] Web Service created
- [ ] Environment set to Docker
- [ ] Dockerfile path set correctly
- [ ] Service deployed successfully
- [ ] API URL tested
- [ ] Ready for n8n!

## Support

- Render Docs: https://render.com/docs
- Render Status: https://status.render.com
- Your service logs: Render Dashboard → Your Service → Logs

