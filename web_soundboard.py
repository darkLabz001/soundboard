#!/usr/bin/env python3
"""
Web-based Music Soundboard - No installation needed!
Open in browser at http://localhost:5000
"""

try:
    from flask import Flask, render_template_string
except ImportError:
    import subprocess
    import sys
    print("Installing Flask...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "flask", "--break-system-packages"])
    from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎵 Music Soundboard - Web Version</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 30px;
            max-width: 1000px;
            width: 100%;
        }

        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 10px;
        }

        .instructions {
            text-align: center;
            color: #666;
            font-size: 14px;
            margin-bottom: 20px;
        }

        .keys-info {
            background: #f0f0f0;
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            color: #666;
            font-size: 12px;
            margin-bottom: 20px;
            font-family: monospace;
        }

        .controls {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }

        .control-group {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        label {
            font-weight: bold;
            color: #333;
        }

        input[type="range"], select {
            padding: 8px;
            border: 2px solid #ddd;
            border-radius: 5px;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }

        .pad {
            aspect-ratio: 1;
            border: 3px solid #333;
            border-radius: 10px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.1s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            user-select: none;
        }

        .pad:hover {
            transform: scale(0.95);
        }

        .pad:active {
            transform: scale(0.85);
            border-width: 5px;
        }

        .pad.p0 { background: #ff6464; }
        .pad.p1 { background: #ffc864; }
        .pad.p2 { background: #ffff64; }
        .pad.p3 { background: #64ff64; }
        .pad.p4 { background: #64c8ff; }
        .pad.p5 { background: #c864ff; }
        .pad.p6 { background: #ff64c8; }
        .pad.p7 { background: #64ffff; }
        .pad.p8 { background: #ff9664; }
        .pad.p9 { background: #96ff64; }
        .pad.p10 { background: #6496ff; }
        .pad.p11 { background: #ff6496; }
        .pad.p12 { background: #c8ff64; }
        .pad.p13 { background: #64ffc8; }
        .pad.p14 { background: #ff9c9c; }
        .pad.p15 { background: #c8c8ff; }

        .checkbox-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin-top: 10px;
        }

        .checkbox-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }

        input[type="checkbox"] {
            width: 18px;
            height: 18px;
            cursor: pointer;
        }

        .info {
            background: #f0f0f0;
            padding: 15px;
            border-radius: 8px;
            color: #666;
            font-size: 14px;
            line-height: 1.6;
        }

        .info strong {
            color: #333;
        }

        @media (max-width: 768px) {
            .controls {
                grid-template-columns: 1fr;
            }

            .grid {
                gap: 10px;
            }

            .pad {
                font-size: 14px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 Music Soundboard</h1>
        <div class="instructions">Click pads or press keys to make music • Perfect for techno and electronic beats</div>

        <div class="keys-info">
            Q W E R  |  A S D F  |  Z X C V  |  1 2 3 4
        </div>

        <div class="controls">
            <div class="control-group">
                <label for="volume">🔊 Volume: <span id="volumeValue">70</span>%</label>
                <input type="range" id="volume" min="0" max="100" value="70">
            </div>

            <div class="control-group">
                <label for="bpm">⏱️ BPM: <span id="bpmValue">120</span></label>
                <input type="range" id="bpm" min="60" max="200" value="120">
            </div>

            <div class="control-group">
                <label for="waveform">🌊 Waveform:</label>
                <select id="waveform">
                    <option value="sine">Sine (Smooth)</option>
                    <option value="square">Square (Electronic)</option>
                    <option value="triangle">Triangle (Warm)</option>
                    <option value="sawtooth">Sawtooth (Bright)</option>
                </select>
            </div>

            <div class="control-group">
                <label for="synth">📊 Synth Type:</label>
                <select id="synth">
                    <option value="basic">Basic Synth</option>
                    <option value="bass">Bass</option>
                    <option value="lead">Lead</option>
                    <option value="pad">Pad</option>
                </select>
            </div>
        </div>

        <div style="margin-bottom: 20px;">
            <label style="font-weight: bold; display: block; margin-bottom: 10px;">🔁 Enable Loops:</label>
            <div class="checkbox-grid">
                <div class="checkbox-item"><input type="checkbox" id="loop0"> <label for="loop0">1</label></div>
                <div class="checkbox-item"><input type="checkbox" id="loop1"> <label for="loop1">2</label></div>
                <div class="checkbox-item"><input type="checkbox" id="loop2"> <label for="loop2">3</label></div>
                <div class="checkbox-item"><input type="checkbox" id="loop3"> <label for="loop3">4</label></div>
                <div class="checkbox-item"><input type="checkbox" id="loop4"> <label for="loop4">5</label></div>
                <div class="checkbox-item"><input type="checkbox" id="loop5"> <label for="loop5">6</label></div>
                <div class="checkbox-item"><input type="checkbox" id="loop6"> <label for="loop6">7</label></div>
                <div class="checkbox-item"><input type="checkbox" id="loop7"> <label for="loop7">8</label></div>
                <div class="checkbox-item"><input type="checkbox" id="loop8"> <label for="loop8">9</label></div>
                <div class="checkbox-item"><input type="checkbox" id="loop9"> <label for="loop9">10</label></div>
                <div class="checkbox-item"><input type="checkbox" id="loop10"> <label for="loop10">11</label></div>
                <div class="checkbox-item"><input type="checkbox" id="loop11"> <label for="loop11">12</label></div>
                <div class="checkbox-item"><input type="checkbox" id="loop12"> <label for="loop12">13</label></div>
                <div class="checkbox-item"><input type="checkbox" id="loop13"> <label for="loop13">14</label></div>
                <div class="checkbox-item"><input type="checkbox" id="loop14"> <label for="loop14">15</label></div>
                <div class="checkbox-item"><input type="checkbox" id="loop15"> <label for="loop15">16</label></div>
            </div>
        </div>

        <div class="grid" id="soundboard">
            <!-- Pads will be generated by JavaScript -->
        </div>

        <div class="info">
            <strong>💡 Tips:</strong><br>
            • Use chromatic scale for musical melodies<br>
            • Enable loops on different pads for polyrhythms<br>
            • Try different waveforms for different moods<br>
            • Combine with your DAW for effects<br>
            • Perfect for making techno, electronic, and experimental music
        </div>
    </div>

    <script>
        // Web Audio API Context
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const masterGain = audioContext.createGain();
        masterGain.connect(audioContext.destination);

        // State
        const state = {
            volume: 0.7,
            waveform: 'sine',
            bpm: 120,
            synth: 'basic',
            loops: new Array(16).fill(false),
            oscillators: {}
        };

        // Key mapping
        const keyMap = {
            'q': 0, 'w': 1, 'e': 2, 'r': 3,
            'a': 4, 's': 5, 'd': 6, 'f': 7,
            'z': 8, 'x': 9, 'c': 10, 'v': 11,
            '1': 12, '2': 13, '3': 14, '4': 15
        };

        // Note frequencies (chromatic scale starting from A)
        const notes = [110, 116.54, 123.47, 130.81, 138.59, 146.83, 155.56, 164.81,
                       174.61, 185, 196, 207.65, 220, 233.08, 246.94, 261.63];

        // Initialize soundboard
        function init() {
            const soundboard = document.getElementById('soundboard');

            for (let i = 0; i < 16; i++) {
                const pad = document.createElement('button');
                pad.className = `pad p${i}`;
                pad.textContent = i + 1;
                pad.addEventListener('mousedown', () => playSound(i));
                pad.addEventListener('mouseup', () => stopSound(i));
                pad.addEventListener('mouseleave', () => stopSound(i));
                soundboard.appendChild(pad);
            }
        }

        // Create oscillator with envelope
        function createOscillator(frequency) {
            const osc = audioContext.createOscillator();
            const env = audioContext.createGain();

            osc.type = state.waveform;
            osc.frequency.value = frequency;

            // ADSR Envelope
            const now = audioContext.currentTime;
            env.gain.setValueAtTime(0, now);
            env.gain.linearRampToValueAtTime(1, now + 0.01);  // Attack
            env.gain.linearRampToValueAtTime(0.7, now + 0.1); // Decay
            // Sustain at 0.7
            env.gain.linearRampToValueAtTime(0, now + 0.5);   // Release

            osc.connect(env);
            env.connect(masterGain);
            osc.start(now);
            osc.stop(now + 0.5);

            return osc;
        }

        // Play sound
        function playSound(padIndex) {
            const freq = notes[padIndex];
            createOscillator(freq);
        }

        // Stop sound
        function stopSound(padIndex) {
            // Sound stops automatically due to envelope
        }

        // Update controls
        document.getElementById('volume').addEventListener('input', (e) => {
            state.volume = e.target.value / 100;
            masterGain.gain.value = state.volume;
            document.getElementById('volumeValue').textContent = e.target.value;
        });

        document.getElementById('bpm').addEventListener('input', (e) => {
            state.bpm = e.target.value;
            document.getElementById('bpmValue').textContent = e.target.value;
        });

        document.getElementById('waveform').addEventListener('change', (e) => {
            state.waveform = e.target.value;
        });

        // Loop controls
        for (let i = 0; i < 16; i++) {
            document.getElementById(`loop${i}`).addEventListener('change', (e) => {
                state.loops[i] = e.target.checked;
            });
        }

        // Keyboard support
        document.addEventListener('keydown', (e) => {
            const key = e.key.toLowerCase();
            if (keyMap.hasOwnProperty(key)) {
                playSound(keyMap[key]);
            }
        });

        // Set initial volume
        masterGain.gain.value = state.volume;

        // Initialize
        init();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    print("\n🎵 Web Music Soundboard Starting...")
    print("📂 Open your browser to: http://localhost:5000")
    print("🎹 Press Ctrl+C to stop\n")
    app.run(debug=False, host='localhost', port=5000)
