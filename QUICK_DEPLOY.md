# Quick Deploy to Render (TL;DR)

## 1. Push to GitHub
```bash
cd C:\Users\USER\cursor-tutor\API_SS
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git branch -M main
git push -u origin main
```

## 2. Deploy on Render
1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your repository
5. Settings:
   - **Name:** `website-screenshot-api`
   - **Environment:** `Docker`
   - **Dockerfile Path:** `Dockerfile`
   - **Instance Type:** `Free`
6. Click "Create Web Service"
7. Wait 10-15 minutes for first build
8. Get your URL: `https://your-app.onrender.com`

## 3. Use in n8n
```
HTTP Request Node:
URL: https://your-app.onrender.com/screenshot?url={{$json.url}}
Method: GET
Response Format: File
Binary Data: true
```

## Done! 🎉

See `DEPLOY_RENDER.md` for detailed instructions.

