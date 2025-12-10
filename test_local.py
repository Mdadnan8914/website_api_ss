"""
Simple test script to test the API locally
Run this after starting the server with: python app.py
"""
import requests
import json
import base64
from pathlib import Path
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# API base URL
BASE_URL = "http://localhost:8000"

def test_single_screenshot():
    """Test single page screenshot"""
    print("Testing single page screenshot...")
    
    response = requests.post(
        f"{BASE_URL}/screenshot",
        json={
            "url": "https://example.com",
            "wait_time": 2000,
            "viewport_width": 1920,
            "viewport_height": 1080
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Success! Screenshot taken of: {data['url']}")
        print(f"  Timestamp: {data['timestamp']}")
        print(f"  Base64 length: {len(data['screenshot_base64'])} characters")
        
        # Optionally save the screenshot
        save_screenshot = input("Save screenshot to file? (y/n): ")
        if save_screenshot.lower() == 'y':
            screenshot_bytes = base64.b64decode(data['screenshot_base64'])
            output_path = Path("screenshot_example.png")
            output_path.write_bytes(screenshot_bytes)
            print(f"  Saved to: {output_path}")
    else:
        print(f"[ERROR] Error: {response.status_code}")
        print(response.text)


def test_all_pages_screenshot():
    """Test all pages screenshot (crawling)"""
    print("\nTesting all pages screenshot (this may take a while)...")
    
    url = input("Enter website URL to crawl (or press Enter for example.com): ").strip()
    if not url:
        url = "https://example.com"
    
    max_pages = input("Max pages to crawl (default 5): ").strip()
    max_pages = int(max_pages) if max_pages.isdigit() else 5
    
    response = requests.post(
        f"{BASE_URL}/screenshot-all",
        json={
            "url": url,
            "wait_time": 2000,
            "viewport_width": 1920,
            "viewport_height": 1080,
            "max_pages": max_pages
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n[OK] Success!")
        print(f"  Base URL: {data['base_url']}")
        print(f"  Total pages: {data['total_pages']}")
        print(f"  Crawl time: {data['crawl_time']}")
        print(f"\n  Pages screenshotted:")
        for i, screenshot in enumerate(data['screenshots'], 1):
            print(f"    {i}. {screenshot['url']}")
        
        # Optionally save all screenshots
        save_screenshots = input("\nSave all screenshots to files? (y/n): ")
        if save_screenshots.lower() == 'y':
            output_dir = Path("screenshots")
            output_dir.mkdir(exist_ok=True)
            
            for screenshot in data['screenshots']:
                screenshot_bytes = base64.b64decode(screenshot['screenshot_base64'])
                # Create safe filename from URL
                filename = screenshot['url'].replace('https://', '').replace('http://', '').replace('/', '_')
                filename = filename[:100] + '.png'  # Limit filename length
                output_path = output_dir / filename
                output_path.write_bytes(screenshot_bytes)
                print(f"  Saved: {output_path}")
    else:
        print(f"[ERROR] Error: {response.status_code}")
        print(response.text)


def test_root():
    """Test root endpoint"""
    print("Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    if response.status_code == 200:
        print("[OK] API is running!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"[ERROR] Error: {response.status_code}")


if __name__ == "__main__":
    print("=" * 50)
    print("Website Screenshot API - Local Test Script")
    print("=" * 50)
    print("\nMake sure the API is running: python app.py")
    print()
    
    # Test root endpoint first
    try:
        test_root()
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to API. Make sure it's running on http://localhost:8000")
        exit(1)
    
    print("\n" + "=" * 50)
    print("Choose test:")
    print("1. Single page screenshot")
    print("2. All pages screenshot (crawl)")
    print("=" * 50)
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_single_screenshot()
    elif choice == "2":
        test_all_pages_screenshot()
    else:
        print("Invalid choice")

