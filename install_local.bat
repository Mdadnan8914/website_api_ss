@echo off
echo Installing Website Screenshot API dependencies...
echo.

REM Upgrade pip first
python -m pip install --upgrade pip

REM Install dependencies using pre-built wheels
pip install --only-binary :all: fastapi uvicorn[standard] playwright beautifulsoup4 requests python-multipart pydantic

REM If the above fails, try without --only-binary flag
if errorlevel 1 (
    echo.
    echo Retrying without wheel-only restriction...
    pip install fastapi uvicorn[standard] playwright beautifulsoup4 requests python-multipart pydantic
)

REM Install Playwright browsers
echo.
echo Installing Playwright browsers...
python -m playwright install chromium

echo.
echo Installation complete!
echo.
echo To run the server, use: python app.py

