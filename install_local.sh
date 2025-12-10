#!/bin/bash
echo "Installing Website Screenshot API dependencies..."
echo

# Upgrade pip first
python3 -m pip install --upgrade pip

# Install dependencies
pip install fastapi uvicorn[standard] playwright beautifulsoup4 requests python-multipart pydantic

# Install Playwright browsers
echo
echo "Installing Playwright browsers..."
python3 -m playwright install chromium

echo
echo "Installation complete!"
echo
echo "To run the server, use: python app.py"

