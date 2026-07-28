# 🎵 Music Soundboard - Keyboard-Controlled Sampler

A Python-based music soundboard for making techno, electronic, and experimental music using your laptop keyboard.

## Features

- **16 Sound Pads** - 4x4 grid controlled by keyboard
- **Multiple Waveforms** - Sine, Square, Triangle, Sawtooth
- **Chromatic Scale** - Each pad plays a different note
- **Loop Function** - Enable looping for continuous playback
- **Volume Control** - Adjust master volume
- **BPM Control** - Set tempo for your music
- **Load Samples** - Import custom WAV files
- **Real-time Mixing** - Layer multiple sounds

## Keyboard Mapping

```
Q  W  E  R          (Row 1)
A  S  D  F          (Row 2)
Z  X  C  V          (Row 3)
1  2  3  4          (Row 4)
```

## Installation & Running

### Quick Start (Recommended)
```bash
chmod +x run_soundboard.sh
./run_soundboard.sh
```

This will automatically:
1. Create a virtual environment
2. Install dependencies (PyQt6, numpy, pyaudio)
3. Launch the soundboard

### Manual Installation
```bash
python3 -m venv soundboard_venv
source soundboard_venv/bin/activate  # On Windows: soundboard_venv\Scripts\activate
pip install PyQt6 numpy pyaudio
python3 soundboard_app.py
```

## How to Use

### Making Sounds
1. **Click buttons** or **press keyboard keys** to trigger sounds
2. Each pad plays a different note in chromatic scale
3. Press and hold to sustain notes

### Loops
1. Check the **checkbox** next to a pad number to enable looping
2. The sound will repeat continuously
3. Uncheck to stop looping

### Changing Waveforms
1. Use the **Waveform selector** dropdown
2. Choose: Sine (smooth), Square (electronic), Triangle (warm), Sawtooth (bright)
3. All pads update to the new waveform

### Loading Custom Samples
1. Click **"Load Sound File..."**
2. Select a WAV file from your computer
3. The first available pad will load the sample
4. Press the pad's key to play it

### Volume & Speed
- **Volume Slider**: Adjust output volume (0-100%)
- **BPM Control**: Set the tempo (60-200 BPM)

## Making Music Tips

### Techno
- Use **Square** or **Sawtooth** waveforms
- Combine bass notes (left side) with hi-hats (right side)
- Enable loops on multiple pads for polyrhythms
- Keep tempo between 120-140 BPM

### Ambient
- Use **Sine** or **Triangle** waveforms
- Load reverb-processed samples
- Long sustained loops create atmospheres
- Try 60-90 BPM

### Experimental
- Mix different waveforms on different pads
- Rapid key pressing creates glitchy effects
- Load unconventional samples
- Variable BPM creates interesting rhythms

## Audio Features

- **Sample Rate**: 44.1 kHz
- **Channels**: Mono
- **Format**: 16-bit PCM
- **ADSR Envelope**: Automatic attack/decay/sustain/release
- **Soft Clipping**: Prevents digital distortion

## Troubleshooting

### No Sound?
- Check volume slider is above 0%
- Make sure your audio output is working
- Try a different waveform

### App Won't Start?
- Make sure Python 3.8+ is installed
- Try manual installation (see above)
- On Linux: `sudo apt-get install python3-dev portaudio19-dev`

### Can't Load Sounds?
- Make sure the file is in WAV format (.wav)
- File should be 44.1 kHz or will be resampled
- Try smaller files first

## Tips for Best Results

1. **Layer Sounds** - Enable loops on different pads with different notes
2. **Humanize** - Manually vary timing by not holding keys too long
3. **Mix Waveforms** - Different pads with different waveforms
4. **Record Output** - Use OBS or your DAW to record the soundboard output
5. **External Input** - Route through a DAW for effects/processing

## Demo Use Cases

- **Live Performance** - Use for interactive live music
- **Jam Sessions** - Quick improvisation with friends
- **Learning** - Understand music basics and waveforms
- **Beat Making** - Create drum patterns and loops
- **Experimental** - Abstract sound design

## Advanced Features

- Double-click buttons for emphasis
- Rapidly toggle waveforms for sound effects
- Load different samples per pad
- Combine with your DAW for processing

---

**Made with Python, PyQt6, and NumPy** 🎹

Enjoy making music! 🎵
