# Quick Start Guide

## ✅ Setup Complete!

Your API is ready to use. Here's what to do next:

## 1. Start the Server

Open a terminal in this directory and run:

```bash
python app.py
```

The server will start at: `http://localhost:8000`

## 2. Test the API

### Option A: Use the Test Script
```bash
python test_local.py
```

### Option B: Test Manually with curl/PowerShell

**Single Page Screenshot:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/screenshot" -Method POST -ContentType "application/json" -Body '{"url":"https://example.com"}'
```

**All Pages Screenshot:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/screenshot-all" -Method POST -ContentType "application/json" -Body '{"url":"https://example.com","max_pages":5}'
```

### Option C: Use a Browser
Open: http://localhost:8000

You'll see the API documentation.

## 3. Use in n8n

Once you deploy to Render, use it in n8n:

1. Add an **HTTP Request** node
2. Set:
   - **Method:** POST
   - **URL:** `https://your-app.onrender.com/screenshot-all`
   - **Body:** JSON
   ```json
   {
     "url": "https://example.com",
     "max_pages": 50
   }
   ```
3. The response will contain base64 screenshots

## 4. Deploy to Render

1. Push code to GitHub/GitLab
2. Create new Web Service on Render
3. Connect repository
4. Settings:
   - **Environment:** Docker
   - **Dockerfile Path:** `Dockerfile`
   - **Port:** `8000`
5. Deploy!

## API Endpoints

- `GET /` - API info
- `POST /screenshot` - Single page screenshot
- `POST /screenshot-all` - All pages screenshot (crawls website)

## Example Request Body

```json
{
  "url": "https://example.com",
  "wait_time": 3000,
  "viewport_width": 1920,
  "viewport_height": 1080,
  "max_pages": 50
}
```

## Need Help?

- Check `README.md` for full documentation
- Run `python test_local.py` to test locally
- Make sure server is running before testing!

