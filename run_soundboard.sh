#!/bin/bash
# Simple soundboard launcher - NO VENV!

echo "🎵 Music Soundboard"
echo "===================="
echo ""
echo "📥 Installing dependencies..."
python3 -m pip install --break-system-packages -q pygame PyQt6 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✓ Ready!"
else
    echo "⚠️ Trying user install..."
    python3 -m pip install --user -q pygame PyQt6 2>/dev/null
fi

echo ""
echo "🎹 Starting Soundboard..."
echo "===================="
echo "📍 Keys: Q W E R / A S D F / Z X C V / 1 2 3 4"
echo "🎙️ Click RED button to record"
echo "📁 Recordings saved as WAV files"
echo ""

python3 "$(dirname "$0")/soundboard_simple.py"
