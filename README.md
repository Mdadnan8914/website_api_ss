# Website Screenshot API for n8n

A FastAPI-based service that crawls websites and takes screenshots of all pages, designed for use with n8n workflows.

## Features

- 🖼️ Take screenshots of single pages or entire websites
- 🕷️ Automatic website crawling to find all internal pages
- 📦 Returns base64-encoded screenshots for easy integration
- 🐳 Dockerized for easy deployment on Render
- ⚡ Fast and efficient with Playwright

## Local Setup

### Prerequisites

- Python 3.11 or higher
- pip

### Installation

1. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On Linux/Mac:
   source venv/bin/activate
   ```

2. **Install dependencies:**
   
   **Option A - Using install script (Windows):**
   ```bash
   install_local.bat
   ```
   
   **Option B - Using install script (Linux/Mac):**
   ```bash
   chmod +x install_local.sh
   ./install_local.sh
   ```
   
   **Option C - Manual installation:**
   ```bash
   # First upgrade pip
   python -m pip install --upgrade pip
   
   # Then install dependencies
   pip install -r requirements.txt
   ```
   
   **If you encounter Rust compilation errors:**
   - Try: `pip install --only-binary :all: -r requirements.txt`
   - Or install Rust from https://rustup.rs/ (if you need to build from source)

3. **Install Playwright browsers:**
   ```bash
   python -m playwright install chromium
   ```
   
   **Note:** On Windows, use `python -m playwright` instead of just `playwright`

4. **Run the application:**
   ```bash
   python app.py
   ```

   Or using uvicorn directly:
   ```bash
   uvicorn app:app --reload
   ```

The API will be available at `http://localhost:8000`

## API Endpoints

### Simple Endpoints (For n8n - Returns Binary Images) ⭐

**GET** `/screenshot?url=...` - Single page screenshot (returns PNG binary)  
**POST** `/screenshot-binary` - Single page screenshot (JSON body, returns PNG binary)  
**POST** `/screenshot-all-binary` - All pages screenshot (returns ZIP file with PNGs)

### Legacy Endpoints (Returns Base64 JSON)

### 1. Single Page Screenshot

**POST** `/screenshot`

Take a screenshot of a single page.

**Request Body:**
```json
{
  "url": "https://example.com",
  "wait_time": 3000,
  "viewport_width": 1920,
  "viewport_height": 1080
}
```

**Response:**
```json
{
  "url": "https://example.com",
  "screenshot_base64": "iVBORw0KGgoAAAANS...",
  "timestamp": "2024-01-01T12:00:00"
}
```

### 2. All Pages Screenshot

**POST** `/screenshot-all`

Crawl website and take screenshots of all pages.

**Request Body:**
```json
{
  "url": "https://example.com",
  "wait_time": 3000,
  "viewport_width": 1920,
  "viewport_height": 1080,
  "max_pages": 50
}
```

**Response:**
```json
{
  "base_url": "https://example.com",
  "total_pages": 5,
  "screenshots": [
    {
      "url": "https://example.com",
      "screenshot_base64": "iVBORw0KGgoAAAANS...",
      "timestamp": "2024-01-01T12:00:00"
    },
    ...
  ],
  "crawl_time": "0:00:15.123456"
}
```

## Testing Locally

### Using curl

**Single page:**
```bash
curl -X POST "http://localhost:8000/screenshot" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

**All pages:**
```bash
curl -X POST "http://localhost:8000/screenshot-all" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "max_pages": 10}'
```

### Using Python requests

```python
import requests

# Single page
response = requests.post(
    "http://localhost:8000/screenshot",
    json={"url": "https://example.com"}
)
print(response.json())

# All pages
response = requests.post(
    "http://localhost:8000/screenshot-all",
    json={"url": "https://example.com", "max_pages": 10}
)
print(response.json())
```

## Deployment on Render

1. **Push your code to GitHub/GitLab**

2. **Create a new Web Service on Render:**
   - Connect your repository
   - Set the following:
     - **Name:** website-screenshot-api
     - **Environment:** Docker
     - **Dockerfile Path:** `Dockerfile`
     - **Port:** `8000`

3. **Deploy:**
   - Render will automatically build and deploy your Docker container

4. **Use in n8n:**
   - Add an HTTP Request node in n8n
   - Set method to `POST`
   - URL: `https://your-render-app.onrender.com/screenshot-all`
   - Body: JSON with your website URL

## Parameters

- `url` (required): The website URL to screenshot
- `wait_time` (optional, default: 3000): Milliseconds to wait after page load for dynamic content
- `viewport_width` (optional, default: 1920): Browser viewport width
- `viewport_height` (optional, default: 1080): Browser viewport height
- `max_pages` (optional, default: 50): Maximum number of pages to crawl and screenshot

## Notes

- The crawler only follows links within the same domain
- Screenshots are full-page (captures entire page, not just viewport)
- Base64 images can be decoded and saved as PNG files
- Large websites may take several minutes to process

## Troubleshooting

**Rust compilation errors during installation:**
- This happens when a package tries to build from source instead of using pre-built wheels
- Solution 1: Upgrade pip first: `python -m pip install --upgrade pip`
- Solution 2: Use the install script: `install_local.bat` (Windows) or `./install_local.sh` (Linux/Mac)
- Solution 3: Install Rust from https://rustup.rs/ if you need to build from source
- Solution 4: Try installing with: `pip install --only-binary :all: -r requirements.txt`

**Playwright browser not found:**
```bash
python -m playwright install chromium
```

**'playwright' is not recognized:**
- Use `python -m playwright install chromium` instead of `playwright install chromium`
- This is the correct way to run Playwright commands on Windows

**Port already in use:**
Change the port in `app.py` or use:
```bash
uvicorn app:app --port 8001
```

**Memory issues with large websites:**
Reduce `max_pages` parameter or process in batches

