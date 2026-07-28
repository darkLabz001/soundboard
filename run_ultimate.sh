#!/bin/bash
echo "🎹 ULTIMATE Music Soundboard"
echo "============================"
echo ""
python3 -m pip install --break-system-packages -q pygame PyQt6 2>/dev/null
echo "✓ Loaded!"
echo ""
echo "🎵 Launching Professional DAW-Style Soundboard..."
echo ""
python3 "$(dirname "$0")/soundboard_ultimate.py"
