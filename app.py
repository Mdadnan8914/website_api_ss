from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, Response, StreamingResponse
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
import base64
import io
from datetime import datetime
import zipfile

app = FastAPI(title="Website Screenshot API", version="1.0.0")


class ScreenshotRequest(BaseModel):
    url: HttpUrl
    wait_time: Optional[int] = 3000  # Wait time in milliseconds for page load
    viewport_width: Optional[int] = 1920
    viewport_height: Optional[int] = 1080
    max_pages: Optional[int] = 50  # Limit number of pages to prevent excessive crawling
    timeout: Optional[int] = 60000  # Navigation timeout in milliseconds (default: 60000)


class SimpleScreenshotRequest(BaseModel):
    url: HttpUrl
    timeout: Optional[int] = 60000  # Navigation timeout in milliseconds (default: 60000)


class ScreenshotResponse(BaseModel):
    url: str
    screenshot_base64: str
    timestamp: str


class WebsiteScreenshotsResponse(BaseModel):
    base_url: str
    total_pages: int
    screenshots: List[ScreenshotResponse]
    crawl_time: str


def get_base_url(url: str) -> str:
    """Extract base URL from full URL"""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def get_domain(url: str) -> str:
    """Extract domain from URL"""
    parsed = urlparse(url)
    return parsed.netloc


async def crawl_website(start_url: str, base_domain: str, max_pages: int = 50) -> List[str]:
    """
    Crawl website to find all internal pages
    Returns list of unique URLs
    """
    visited = set()
    to_visit = [start_url]
    all_urls = [start_url]
    
    while to_visit and len(visited) < max_pages:
        current_url = to_visit.pop(0)
        
        if current_url in visited:
            continue
            
        visited.add(current_url)
        
        try:
            # Fetch page content
            response = requests.get(current_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            # Parse HTML to find links
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all anchor tags
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(current_url, href)
                
                # Only include URLs from the same domain
                if get_domain(absolute_url) == base_domain:
                    # Remove fragments (#)
                    absolute_url = absolute_url.split('#')[0]
                    
                    if absolute_url not in visited and absolute_url not in to_visit:
                        if len(visited) + len(to_visit) < max_pages:
                            to_visit.append(absolute_url)
                            all_urls.append(absolute_url)
        
        except Exception as e:
            print(f"Error crawling {current_url}: {str(e)}")
            continue
    
    return list(visited)


async def take_screenshot(
    url: str,
    wait_time: int = 3000,
    viewport_width: int = 1920,
    viewport_height: int = 1080,
    timeout: int = 60000
) -> bytes:
    """
    Take screenshot of a single page and return as bytes (binary)
    """
    async with async_playwright() as p:
        # Launch browser with realistic settings to avoid detection
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        
        # Create context with realistic user agent and viewport
        context = await browser.new_context(
            viewport={'width': viewport_width, 'height': viewport_height},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York'
        )
        page = await context.new_page()
        
        try:
            # Try multiple wait strategies as fallback
            wait_strategies = ['load', 'domcontentloaded', 'commit']
            last_error = None
            
            for wait_strategy in wait_strategies:
                try:
                    # Navigate to page with current wait strategy
                    response = await page.goto(url, wait_until=wait_strategy, timeout=timeout)
                    
                    # Check if page loaded successfully
                    if response and response.status >= 400:
                        raise Exception(f"Page returned status {response.status}: {response.status_text}")
                    
                    # Wait additional time for dynamic content to render
                    await page.wait_for_timeout(wait_time)
                    
                    # Check if page shows an error (common error indicators)
                    page_title = await page.title()
                    page_url = page.url
                    
                    # Take screenshot
                    screenshot_bytes = await page.screenshot(full_page=True)
                    
                    return screenshot_bytes
                    
                except Exception as e:
                    last_error = e
                    # If this isn't the last strategy, try the next one
                    if wait_strategy != wait_strategies[-1]:
                        print(f"Wait strategy '{wait_strategy}' failed, trying next...")
                        continue
                    else:
                        # Last strategy failed, raise the error
                        raise
            
            # If we get here, all strategies failed
            raise last_error if last_error else Exception("All wait strategies failed")
        
        except Exception as e:
            # Provide more detailed error information
            error_msg = str(e)
            try:
                current_url = page.url
                page_title = await page.title()
                error_msg += f" | Current URL: {current_url} | Page Title: {page_title}"
            except:
                pass
            raise Exception(f"Error taking screenshot of {url}: {error_msg}")
        
        finally:
            await browser.close()


async def take_screenshot_base64(
    url: str,
    wait_time: int = 3000,
    viewport_width: int = 1920,
    viewport_height: int = 1080,
    timeout: int = 60000
) -> str:
    """
    Take screenshot of a single page and return as base64 (for backward compatibility)
    """
    screenshot_bytes = await take_screenshot(url, wait_time, viewport_width, viewport_height, timeout)
    return base64.b64encode(screenshot_bytes).decode('utf-8')


@app.get("/")
async def root():
    return {
        "message": "Website Screenshot API",
        "status": "running",
        "endpoints": {
            "GET /health": "Health check endpoint (use to wake up service on Render)",
            "GET /screenshot?url=...": "Take screenshot (returns PNG binary) - SIMPLE FOR N8N",
            "POST /screenshot-binary": "Take screenshot (JSON body with url, returns PNG binary) - SIMPLE FOR N8N",
            "POST /screenshot": "Take screenshot (returns base64 JSON) - legacy",
            "POST /screenshot-all": "Take screenshots of all pages (returns base64 JSON) - legacy",
            "POST /screenshot-all-binary": "Take screenshots of all pages (returns ZIP file) - FOR N8N"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint - use this to wake up the service on Render
    Returns 200 OK when service is ready
    """
    return {
        "status": "healthy",
        "message": "Service is running and ready to take screenshots"
    }


@app.get("/screenshot")
async def screenshot_simple_get(
    url: str = Query(..., description="Website URL to screenshot"),
    timeout: Optional[int] = Query(60000, description="Navigation timeout in milliseconds (default: 60000)")
):
    """
    SIMPLE ENDPOINT FOR N8N: Just pass URL as query parameter
    Returns PNG image binary - ready to pass to GPT module
    
    Usage: GET /screenshot?url=https://example.com
    Optional: GET /screenshot?url=https://example.com&timeout=90000
    """
    try:
        screenshot_bytes = await take_screenshot(str(url), timeout=timeout)
        
        return Response(
            content=screenshot_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": f'inline; filename="screenshot.png"'
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/screenshot-binary")
async def screenshot_simple_post(request: SimpleScreenshotRequest):
    """
    SIMPLE ENDPOINT FOR N8N: Just pass URL in JSON body
    Returns PNG image binary - ready to pass to GPT module
    
    Usage: POST /screenshot-binary
    Body: {"url": "https://example.com"}
    Optional: {"url": "https://example.com", "timeout": 90000}
    """
    try:
        screenshot_bytes = await take_screenshot(str(request.url), timeout=request.timeout)
        
        return Response(
            content=screenshot_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": f'inline; filename="screenshot.png"'
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/screenshot", response_model=ScreenshotResponse)
async def screenshot_single_page(request: ScreenshotRequest):
    """
    Take screenshot of a single page (returns base64 JSON - for backward compatibility)
    """
    try:
        screenshot_base64 = await take_screenshot_base64(
            str(request.url),
            request.wait_time,
            request.viewport_width,
            request.viewport_height
        )
        
        return ScreenshotResponse(
            url=str(request.url),
            screenshot_base64=screenshot_base64,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/screenshot-all", response_model=WebsiteScreenshotsResponse)
async def screenshot_all_pages(request: ScreenshotRequest):
    """
    Crawl website and take screenshots of all pages (returns base64 JSON - for backward compatibility)
    """
    start_time = datetime.now()
    base_url = str(request.url)
    base_domain = get_domain(base_url)
    
    try:
        # Step 1: Crawl website to find all pages
        print(f"Crawling website: {base_url}")
        all_urls = await crawl_website(base_url, base_domain, request.max_pages)
        print(f"Found {len(all_urls)} pages to screenshot")
        
        # Step 2: Take screenshots of all pages
        screenshots = []
        for url in all_urls:
            try:
                print(f"Taking screenshot of: {url}")
                screenshot_base64 = await take_screenshot_base64(
                    url,
                    request.wait_time,
                    request.viewport_width,
                    request.viewport_height,
                    request.timeout
                )
                
                screenshots.append(ScreenshotResponse(
                    url=url,
                    screenshot_base64=screenshot_base64,
                    timestamp=datetime.now().isoformat()
                ))
            except Exception as e:
                print(f"Failed to screenshot {url}: {str(e)}")
                continue
        
        end_time = datetime.now()
        crawl_time = str(end_time - start_time)
        
        return WebsiteScreenshotsResponse(
            base_url=base_url,
            total_pages=len(screenshots),
            screenshots=screenshots,
            crawl_time=crawl_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/screenshot-all-binary")
async def screenshot_all_pages_binary(request: ScreenshotRequest):
    """
    SIMPLE ENDPOINT FOR N8N: Crawl website and return all screenshots as ZIP file
    Returns ZIP file with PNG images - ready to extract and pass to GPT module
    """
    start_time = datetime.now()
    base_url = str(request.url)
    base_domain = get_domain(base_url)
    
    try:
        # Step 1: Crawl website to find all pages
        print(f"Crawling website: {base_url}")
        all_urls = await crawl_website(base_url, base_domain, request.max_pages)
        print(f"Found {len(all_urls)} pages to screenshot")
        
        # Step 2: Create ZIP file in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Step 3: Take screenshots of all pages and add to ZIP
            for url in all_urls:
                try:
                    print(f"Taking screenshot of: {url}")
                    screenshot_bytes = await take_screenshot(
                        url,
                        request.wait_time,
                        request.viewport_width,
                        request.viewport_height,
                        request.timeout
                    )
                    
                    # Create safe filename from URL
                    filename = url.replace('https://', '').replace('http://', '').replace('/', '_')
                    filename = filename[:100] + '.png'  # Limit filename length
                    
                    zip_file.writestr(filename, screenshot_bytes)
                    
                except Exception as e:
                    print(f"Failed to screenshot {url}: {str(e)}")
                    continue
        
        zip_buffer.seek(0)
        
        end_time = datetime.now()
        crawl_time = str(end_time - start_time)
        print(f"Completed in {crawl_time}")
        
        return Response(
            content=zip_buffer.getvalue(),
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="screenshots.zip"'
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

