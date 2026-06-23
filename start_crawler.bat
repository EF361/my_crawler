@echo off
title Web Crawler
echo =========================================
echo    Web Crawler - Startup
echo =========================================
echo.

:: 1. Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed on this computer!
    echo Please download and install Python from https://www.python.org/
    echo IMPORTANT: Make sure to check the box "Add Python to PATH" during installation.
    pause
    exit /b
)

:: 2. Create the Virtual Environment (The Sandbox)
if not exist "venv\Scripts\activate" (
    echo [INFO] First time setup: Creating an isolated virtual environment...
    python -m venv venv
)

:: 3. Activate the Sandbox
echo [INFO] Activating the virtual environment...
call venv\Scripts\activate

:: 4. Install and Update Dependencies
echo [INFO] Upgrading package manager...
python -m pip install --upgrade pip -q

echo [INFO] Installing required AI and scraping libraries...
pip install -r requirements.txt -q

:: 5. Launch the App
echo.
echo [INFO] Starting the Crawler! A browser window should open shortly...
echo =========================================
streamlit run app.py

pause