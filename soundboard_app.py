#!/usr/bin/env python3
"""
Music Soundboard - Keyboard-controlled sampler for making techno/electronic music
"""

import sys
import numpy as np
from pathlib import Path
import pyaudio
import threading
import wave
from collections import defaultdict

try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QGridLayout,
                                 QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFileDialog,
                                 QSpinBox, QSlider, QComboBox, QCheckBox)
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
    from PyQt6.QtGui import QFont, QColor, QPalette, QKeyEvent
except ImportError:
    print("Installing PyQt6...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "PyQt6"])
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QGridLayout,
                                 QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFileDialog,
                                 QSpinBox, QSlider, QComboBox, QCheckBox)
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
    from PyQt6.QtGui import QFont, QColor, QPalette, QKeyEvent

class AudioEngine(QObject):
    """Handles audio playback"""
    sound_finished = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.sounds = {}
        self.playing = {}
        self.loop_enabled = defaultdict(bool)
        self.volume = 1.0
        self.bpm = 120
        self.is_recording = False
        self.record_buffer = []

        # PyAudio setup
        self.p = pyaudio.PyAudio()
        self.sample_rate = 44100
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                  channels=1,
                                  rate=self.sample_rate,
                                  output=True,
                                  frames_per_buffer=2048)

        self.mix_buffer = np.zeros(2048, dtype=np.float32)
        self.mixer_thread = threading.Thread(target=self.mixer_loop, daemon=True)
        self.mixer_running = True
        self.mixer_thread.start()

    def mixer_loop(self):
        """Main audio mixing loop"""
        while self.mixer_running:
            self.mix_buffer[:] = 0

            # Mix all playing sounds
            for key, (sound_data, position) in list(self.playing.items()):
                remaining = len(sound_data) - position
                if remaining <= 0:
                    del self.playing[key]
                    if not self.loop_enabled[key]:
                        self.sound_finished.emit(key)
                    continue

                chunk_size = min(2048, remaining)
                chunk = sound_data[position:position+chunk_size]
                self.mix_buffer[:chunk_size] += chunk * self.volume

                if self.loop_enabled[key] and chunk_size < 2048:
                    # Loop sound
                    self.playing[key] = (sound_data, 0)
                else:
                    self.playing[key] = (sound_data, position + chunk_size)

            # Soft clip to prevent distortion
            self.mix_buffer = np.tanh(self.mix_buffer * 0.9)
            self.stream.write(self.mix_buffer.astype(np.float32).tobytes())

    def load_sound(self, key, filepath):
        """Load a WAV file"""
        try:
            with wave.open(filepath, 'rb') as wav_file:
                frames = wav_file.readframes(wav_file.getnframes())
                sound_data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
                self.sounds[key] = sound_data
                return True
        except Exception as e:
            print(f"Error loading sound: {e}")
            return False

    def generate_sound(self, key, frequency, duration=0.5, waveform='sine'):
        """Generate a synth sound"""
        num_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, num_samples)

        if waveform == 'sine':
            sound = np.sin(2 * np.pi * frequency * t)
        elif waveform == 'square':
            sound = np.sign(np.sin(2 * np.pi * frequency * t))
        elif waveform == 'triangle':
            sound = 2 * np.abs(2 * (t * frequency - np.floor(t * frequency + 0.5))) - 1
        elif waveform == 'sawtooth':
            sound = 2 * (t * frequency - np.floor(t * frequency + 0.5))
        else:
            sound = np.sin(2 * np.pi * frequency * t)

        # ADSR envelope
        attack = int(0.01 * self.sample_rate)
        decay = int(0.1 * self.sample_rate)
        sustain_level = 0.7
        release = int(0.2 * self.sample_rate)

        envelope = np.ones(num_samples)
        if attack > 0:
            envelope[:attack] = np.linspace(0, 1, attack)
        if decay > 0 and attack + decay < num_samples:
            envelope[attack:attack+decay] = np.linspace(1, sustain_level, decay)
        if release > 0:
            envelope[-release:] = np.linspace(sustain_level, 0, release)

        sound = sound * envelope * 0.8
        self.sounds[key] = sound

    def play_sound(self, key):
        """Play a sound"""
        if key in self.sounds:
            self.playing[key] = (self.sounds[key], 0)

    def stop_sound(self, key):
        """Stop a sound"""
        if key in self.playing:
            del self.playing[key]

    def set_volume(self, volume):
        """Set master volume (0-1)"""
        self.volume = max(0.0, min(1.0, volume))

    def set_loop(self, key, enabled):
        """Enable/disable looping for a sound"""
        self.loop_enabled[key] = enabled

    def cleanup(self):
        """Clean up audio resources"""
        self.mixer_running = False
        self.mixer_thread.join(timeout=1.0)
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

class SoundboardApp(QMainWindow):
    """Main soundboard application"""

    # Keyboard to grid mapping (QWERTY layout for 4x4 grid)
    KEY_MAP = {
        Qt.Key.Key_Q: (0, 0), Qt.Key.Key_W: (0, 1), Qt.Key.Key_E: (0, 2), Qt.Key.Key_R: (0, 3),
        Qt.Key.Key_A: (1, 0), Qt.Key.Key_S: (1, 1), Qt.Key.Key_D: (1, 2), Qt.Key.Key_F: (1, 3),
        Qt.Key.Key_Z: (2, 0), Qt.Key.Key_X: (2, 1), Qt.Key.Key_C: (2, 2), Qt.Key.Key_V: (2, 3),
        Qt.Key.Key_1: (3, 0), Qt.Key.Key_2: (3, 1), Qt.Key.Key_3: (3, 2), Qt.Key.Key_4: (3, 3),
    }

    def __init__(self):
        super().__init__()
        self.audio_engine = AudioEngine()
        self.buttons = {}
        self.sound_colors = {}
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("🎵 Music Soundboard - Techno Maker")
        self.setGeometry(100, 100, 1200, 800)

        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()

        # Left side: Soundboard grid
        left_layout = QVBoxLayout()

        # Title
        title = QLabel("🎹 SOUNDBOARD")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        left_layout.addWidget(title)

        # Instructions
        instructions = QLabel("Q W E R / A S D F / Z X C V / 1 2 3 4")
        instructions.setFont(QFont("Arial", 10))
        instructions.setStyleSheet("color: #888;")
        left_layout.addWidget(instructions)

        # Grid layout for buttons
        grid = QGridLayout()
        grid.setSpacing(10)

        colors = [
            QColor(255, 100, 100),   # Red
            QColor(255, 200, 100),   # Orange
            QColor(255, 255, 100),   # Yellow
            QColor(100, 255, 100),   # Green
            QColor(100, 200, 255),   # Blue
            QColor(200, 100, 255),   # Purple
            QColor(255, 100, 200),   # Pink
            QColor(100, 255, 255),   # Cyan
            QColor(255, 150, 100),   # Coral
            QColor(150, 255, 100),   # Lime
            QColor(100, 150, 255),   # Light Blue
            QColor(255, 100, 150),   # Rose
            QColor(200, 255, 100),   # Yellow-Green
            QColor(100, 255, 200),   # Mint
            QColor(255, 200, 200),   # Light Red
            QColor(200, 200, 255),   # Lavender
        ]

        color_idx = 0
        for row in range(4):
            for col in range(4):
                btn = QPushButton(f"{row*4+col+1}")
                btn.setMinimumSize(120, 120)
                btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {colors[color_idx].name()};
                        border: 3px solid #333;
                        border-radius: 10px;
                        color: white;
                        font-weight: bold;
                    }}
                    QPushButton:pressed {{
                        background-color: {colors[color_idx].darker(150).name()};
                        border: 5px solid #000;
                    }}
                """)

                key = list(self.KEY_MAP.keys())[row*4+col]
                self.buttons[(row, col)] = btn
                self.sound_colors[(row, col)] = colors[color_idx]

                grid.addWidget(btn, row, col)
                color_idx += 1

                # Generate default synth sound for each button
                note_number = row * 4 + col
                freq = 110 * (2 ** (note_number / 12))  # Chromatic scale
                self.audio_engine.generate_sound((row, col), freq, 0.5, 'sine')

        left_layout.addLayout(grid, 1)

        # Right side: Controls
        right_layout = QVBoxLayout()

        # Volume control
        right_layout.addWidget(QLabel("Volume"))
        volume_slider = QSlider(Qt.Orientation.Horizontal)
        volume_slider.setMinimum(0)
        volume_slider.setMaximum(100)
        volume_slider.setValue(70)
        volume_slider.sliderMoved.connect(lambda v: self.audio_engine.set_volume(v / 100))
        right_layout.addWidget(volume_slider)

        # BPM control
        right_layout.addWidget(QLabel("BPM"))
        bpm_spin = QSpinBox()
        bpm_spin.setMinimum(60)
        bpm_spin.setMaximum(200)
        bpm_spin.setValue(120)
        bpm_spin.valueChanged.connect(lambda v: setattr(self.audio_engine, 'bpm', v))
        right_layout.addWidget(bpm_spin)

        # Waveform selector
        right_layout.addWidget(QLabel("Waveform"))
        waveform_combo = QComboBox()
        waveform_combo.addItems(['sine', 'square', 'triangle', 'sawtooth'])
        waveform_combo.currentTextChanged.connect(self.on_waveform_changed)
        right_layout.addWidget(waveform_combo)

        # Loop control
        right_layout.addWidget(QLabel("Loops"))
        self.loop_checkboxes = {}
        for row in range(4):
            row_layout = QHBoxLayout()
            for col in range(4):
                cb = QCheckBox(f"{row*4+col+1}")
                cb.toggled.connect(lambda checked, r=row, c=col:
                                 self.audio_engine.set_loop((r, c), checked))
                self.loop_checkboxes[(row, col)] = cb
                row_layout.addWidget(cb)
            right_layout.addLayout(row_layout)

        # Load sound button
        right_layout.addWidget(QLabel("Load Samples"))
        load_btn = QPushButton("Load Sound File...")
        load_btn.clicked.connect(self.load_sound)
        right_layout.addWidget(load_btn)

        # Instructions
        right_layout.addStretch()
        info = QLabel(
            "🎵 INSTRUCTIONS\n"
            "• Click buttons or press keys\n"
            "• Check boxes to loop sounds\n"
            "• Change waveform to edit sounds\n"
            "• Load custom samples\n\n"
            "🎹 Great for making:\n"
            "• Techno\n"
            "• Electronic\n"
            "• Experimental\n"
            "• Beat making"
        )
        info.setFont(QFont("Arial", 10))
        info.setStyleSheet("background: #f0f0f0; padding: 10px; border-radius: 5px;")
        right_layout.addWidget(info)

        # Combine layouts
        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 1)
        main_widget.setLayout(main_layout)

        # Connect button clicks
        for (row, col), btn in self.buttons.items():
            btn.pressed.connect(lambda r=row, c=col: self.play_sound(r, c))
            btn.released.connect(lambda r=row, c=col: self.stop_sound(r, c))

    def keyPressEvent(self, event):
        """Handle keyboard input"""
        if event.key() in self.KEY_MAP:
            row, col = self.KEY_MAP[event.key()]
            self.buttons[(row, col)].setDown(True)
            self.play_sound(row, col)

    def keyReleaseEvent(self, event):
        """Handle key release"""
        if event.key() in self.KEY_MAP:
            row, col = self.KEY_MAP[event.key()]
            self.buttons[(row, col)].setDown(False)
            self.stop_sound(row, col)

    def play_sound(self, row, col):
        """Play sound from button"""
        self.audio_engine.play_sound((row, col))
        # Visual feedback
        self.buttons[(row, col)].setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                border: 5px solid {self.sound_colors[(row, col)].name()};
                border-radius: 10px;
                color: black;
                font-weight: bold;
            }}
        """)

    def stop_sound(self, row, col):
        """Stop sound from button"""
        if not self.loop_checkboxes[(row, col)].isChecked():
            self.audio_engine.stop_sound((row, col))
        # Visual feedback reset
        color = self.sound_colors[(row, col)]
        self.buttons[(row, col)].setStyleSheet(f"""
            QPushButton {{
                background-color: {color.name()};
                border: 3px solid #333;
                border-radius: 10px;
                color: white;
                font-weight: bold;
            }}
            QPushButton:pressed {{
                background-color: {color.darker(150).name()};
                border: 5px solid #000;
            }}
        """)

    def load_sound(self):
        """Load a custom sound file"""
        filepath, _ = QFileDialog.getOpenFileName(self, "Load Sound", "", "WAV Files (*.wav)")
        if filepath:
            # Load into the first empty button
            for row in range(4):
                for col in range(4):
                    if (row, col) not in self.audio_engine.sounds or len(self.audio_engine.sounds[(row, col)]) == 0:
                        self.audio_engine.load_sound((row, col), filepath)
                        self.buttons[(row, col)].setText(Path(filepath).stem[:8])
                        return
            print("All buttons filled!")

    def on_waveform_changed(self, waveform):
        """Change waveform for all synth sounds"""
        for row in range(4):
            for col in range(4):
                note_number = row * 4 + col
                freq = 110 * (2 ** (note_number / 12))
                self.audio_engine.generate_sound((row, col), freq, 0.5, waveform)

    def closeEvent(self, event):
        """Clean up on close"""
        self.audio_engine.cleanup()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SoundboardApp()
    window.show()
    sys.exit(app.exec())
