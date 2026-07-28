#!/bin/bash
# Soundboard launcher script

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$SCRIPT_DIR/soundboard_venv"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "🎵 Setting up soundboard environment..."
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    pip install -q PyQt6 numpy pyaudio
    echo "✓ Environment ready!"
else
    source "$VENV_DIR/bin/activate"
fi

# Run the soundboard
echo "🎹 Starting Music Soundboard..."
python3 "$SCRIPT_DIR/soundboard_app.py"
