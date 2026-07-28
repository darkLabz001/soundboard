#!/bin/bash
echo "🎵 Professional Music Soundboard"
echo "================================"
echo ""
echo "📥 Installing dependencies..."
python3 -m pip install --break-system-packages -q pygame PyQt6 2>/dev/null

echo "✓ Ready!"
echo ""
echo "🎵 Starting Professional Soundboard..."
echo "🥁 DRUMS: Q W E R"
echo "🎸 BASS:  A S D F"
echo "🎹 LEAD:  Z X C V"
echo "🌊 PADS:  1 2 3 4"
echo ""

python3 "$(dirname "$0")/soundboard_pro.py"
