#!/bin/bash

echo "🚀 Starting Edge AI Setup..."

# Move into inner project folder
cd Fire_Test

# -----------------------------
# Try creating virtual env
# -----------------------------
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv 2>/dev/null
fi

# -----------------------------
# Activate venv (SAFE)
# -----------------------------
if [ -f "venv/bin/activate" ]; then
    echo "⚙️ Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️ venv not available, continuing without it"
fi

# -----------------------------
# Upgrade pip
# -----------------------------
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# -----------------------------
# Install dependencies
# -----------------------------
echo "📥 Installing dependencies..."
pip install fastapi "uvicorn[standard]"
pip install torch torchvision opencv-python numpy requests

# -----------------------------
# Run server
# -----------------------------
echo "🔥 Starting FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port 8000
