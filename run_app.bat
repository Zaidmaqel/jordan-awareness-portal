@echo off
setlocal enabledelayedexpansion

echo ====================================================================
echo  JSSAA: Jordan Social & Security Awareness Analysis
echo  Launching Streamlit Interactive GUI
echo ====================================================================

REM Check if Python is available
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found in PATH. Please install Python 3.9+ and try again.
    pause
    exit /b 1
)

REM Check or create virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo [INFO] Virtual environment not found. Creating 'venv'...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate.bat
    echo [INFO] Installing project dependencies from requirements.txt...
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Dependency installation encountered an issue.
        pause
        exit /b 1
    )
) else (
    echo [INFO] Activating existing virtual environment...
    call venv\Scripts\activate.bat
)

echo [INFO] Launching Streamlit web interface...
python -m streamlit run app.py

pause
