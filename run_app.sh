#!/usr/bin/env bash
set -e

echo "===================================================================="
echo " JSSAA: Jordan Social & Security Awareness Analysis"
echo " Launching Streamlit Interactive GUI (Linux / macOS)"
echo "===================================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "[ERROR] Python was not found in PATH. Please install Python 3.9+."
        exit 1
    else
        PY_CMD="python"
    fi
else
    PY_CMD="python3"
fi

# Check or create virtual environment
if [ ! -f "venv/bin/activate" ]; then
    echo "[INFO] Virtual environment not found. Creating 'venv'..."
    $PY_CMD -m venv venv
    echo "[INFO] Activating virtual environment..."
    source venv/bin/activate
    echo "[INFO] Installing project dependencies from requirements.txt..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "[INFO] Activating existing virtual environment..."
    source venv/bin/activate
fi

echo "[INFO] Launching Streamlit web interface..."
streamlit run app.py

