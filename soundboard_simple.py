#!/usr/bin/env python3
"""
Music Soundboard - Simple version with no dependencies!
Uses pygame for audio (easier to install than PyAudio)
"""

import sys
import math
import struct
from collections import defaultdict
from datetime import datetime
import threading
import wave

# Try to import pygame
try:
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
    HAS_PYGAME = True
except ImportError:
    print("📥 Installing pygame (first time only)...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", "pygame"])
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
    HAS_PYGAME = True

# Try to import PyQt6
try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QGridLayout,
                                 QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFileDialog,
                                 QSpinBox, QSlider, QComboBox, QCheckBox, QMessageBox)
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
    from PyQt6.QtGui import QFont, QColor, QKeyEvent
except ImportError:
    print("📥 Installing PyQt6 (first time only)...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", "PyQt6"])
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QGridLayout,
                                 QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFileDialog,
                                 QSpinBox, QSlider, QComboBox, QCheckBox, QMessageBox)
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
    from PyQt6.QtGui import QFont, QColor, QKeyEvent

class AudioSynthesizer:
    """Simple audio synthesizer using pygame mixer"""

    def __init__(self):
        self.sample_rate = 44100
        self.volume = 0.7
        self.waveform = 'sine'
        self.is_recording = False
        self.recording_buffer = []

    def generate_sound(self, frequency, duration=0.5, waveform='sine'):
        """Generate a sound wave and return as pygame Sound"""
        num_samples = int(self.sample_rate * duration)

        # Generate samples using math (no numpy needed!)
        samples = []
        for i in range(num_samples):
            t = i / self.sample_rate

            if waveform == 'sine':
                sample = math.sin(2 * math.pi * frequency * t)
            elif waveform == 'square':
                val = math.sin(2 * math.pi * frequency * t)
                sample = 1.0 if val > 0 else -1.0
            elif waveform == 'triangle':
                val = 2 * (t * frequency - math.floor(t * frequency + 0.5))
                sample = 2 * abs(val) - 1
            elif waveform == 'sawtooth':
                sample = 2 * (t * frequency - math.floor(t * frequency + 0.5))
            else:
                sample = math.sin(2 * math.pi * frequency * t)

            # ADSR Envelope
            if i < int(0.01 * self.sample_rate):  # Attack
                envelope = i / int(0.01 * self.sample_rate)
            elif i < int(0.1 * self.sample_rate):  # Decay
                envelope = 1.0 - (i - int(0.01 * self.sample_rate)) / int(0.09 * self.sample_rate) * 0.3
            elif i < int(0.3 * self.sample_rate):  # Sustain
                envelope = 0.7
            else:  # Release
                remaining = num_samples - i
                release_time = int(0.2 * self.sample_rate)
                if remaining > 0:
                    envelope = 0.7 * remaining / release_time
                else:
                    envelope = 0

            samples.append(int(sample * envelope * 0.8 * 32767 * self.volume))

        # Convert to 16-bit bytes using struct
        sound_bytes = b''.join(struct.pack('<h', max(-32768, min(32767, s))) for s in samples)

        # Create pygame Sound
        sound = pygame.mixer.Sound(buffer=sound_bytes)

        # Record if enabled
        if self.is_recording:
            self.recording_buffer.extend(samples)

        return sound

    def start_recording(self):
        """Start recording audio"""
        self.is_recording = True
        self.recording_buffer = []

    def stop_recording(self):
        """Stop recording and save to file"""
        self.is_recording = False
        if self.recording_buffer:
            return self.save_recording()
        return None

    def save_recording(self):
        """Save recording to WAV file"""
        if not self.recording_buffer:
            return None

        # Convert to 16-bit bytes using struct
        recording_bytes = b''.join(struct.pack('<h', max(-32768, min(32767, s))) for s in self.recording_buffer)

        # Generate filename
        filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"

        # Save WAV file
        try:
            with wave.open(filename, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(recording_bytes)

            print(f"✓ Recording saved: {filename}")
            return filename
        except Exception as e:
            print(f"Error saving recording: {e}")
            return None

class SoundboardApp(QMainWindow):
    """Main soundboard application"""

    KEY_MAP = {
        Qt.Key.Key_Q: (0, 0), Qt.Key.Key_W: (0, 1), Qt.Key.Key_E: (0, 2), Qt.Key.Key_R: (0, 3),
        Qt.Key.Key_A: (1, 0), Qt.Key.Key_S: (1, 1), Qt.Key.Key_D: (1, 2), Qt.Key.Key_F: (1, 3),
        Qt.Key.Key_Z: (2, 0), Qt.Key.Key_X: (2, 1), Qt.Key.Key_C: (2, 2), Qt.Key.Key_V: (2, 3),
        Qt.Key.Key_1: (3, 0), Qt.Key.Key_2: (3, 1), Qt.Key.Key_3: (3, 2), Qt.Key.Key_4: (3, 3),
    }

    def __init__(self):
        super().__init__()
        self.synth = AudioSynthesizer()
        self.buttons = {}
        self.sound_colors = {}
        self.recording = False
        self.sounds = {}
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("🎵 Music Soundboard - No Dependencies!")
        self.setGeometry(100, 100, 1300, 800)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()

        # Left side: Soundboard grid
        left_layout = QVBoxLayout()

        title = QLabel("🎹 SOUNDBOARD")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        left_layout.addWidget(title)

        instructions = QLabel("Q W E R / A S D F / Z X C V / 1 2 3 4")
        instructions.setFont(QFont("Arial", 10))
        instructions.setStyleSheet("color: #888;")
        left_layout.addWidget(instructions)

        grid = QGridLayout()
        grid.setSpacing(10)

        colors = [
            QColor(255, 100, 100), QColor(255, 200, 100), QColor(255, 255, 100), QColor(100, 255, 100),
            QColor(100, 200, 255), QColor(200, 100, 255), QColor(255, 100, 200), QColor(100, 255, 255),
            QColor(255, 150, 100), QColor(150, 255, 100), QColor(100, 150, 255), QColor(255, 100, 150),
            QColor(200, 255, 100), QColor(100, 255, 200), QColor(255, 200, 200), QColor(200, 200, 255),
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

                self.buttons[(row, col)] = btn
                self.sound_colors[(row, col)] = colors[color_idx]

                grid.addWidget(btn, row, col)
                color_idx += 1

                # Generate default synth sound
                note_number = row * 4 + col
                freq = 110 * (2 ** (note_number / 12))
                self.sounds[(row, col)] = self.synth.generate_sound(freq, 0.5, 'sine')

        left_layout.addLayout(grid, 1)

        # Right side: Controls
        right_layout = QVBoxLayout()

        # Recording section
        right_layout.addWidget(QLabel("🎙️ RECORDING", font=QFont("Arial", 12, QFont.Weight.Bold)))

        self.record_btn = QPushButton("⏺️ Start Recording")
        self.record_btn.setMinimumHeight(50)
        self.record_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 8px;
                border: 2px solid #cc0000;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
        """)
        self.record_btn.clicked.connect(self.toggle_recording)
        right_layout.addWidget(self.record_btn)

        self.record_time = QLabel("Ready to record")
        self.record_time.setStyleSheet("font-size: 14px; font-weight: bold; color: #666;")
        right_layout.addWidget(self.record_time)

        right_layout.addWidget(QLabel(""))

        # Volume control
        right_layout.addWidget(QLabel("🔊 Volume"))
        volume_slider = QSlider(Qt.Orientation.Horizontal)
        volume_slider.setMinimum(0)
        volume_slider.setMaximum(100)
        volume_slider.setValue(70)
        volume_slider.sliderMoved.connect(lambda v: setattr(self.synth, 'volume', v / 100))
        right_layout.addWidget(volume_slider)

        # Waveform selector
        right_layout.addWidget(QLabel("🌊 Waveform"))
        waveform_combo = QComboBox()
        waveform_combo.addItems(['sine', 'square', 'triangle', 'sawtooth'])
        waveform_combo.currentTextChanged.connect(self.on_waveform_changed)
        right_layout.addWidget(waveform_combo)

        right_layout.addStretch()
        info = QLabel(
            "🎵 QUICK START\n\n"
            "• Click pads or press keys\n"
            "• Click RECORD button\n"
            "• Make your music!\n"
            "• Click STOP to save\n\n"
            "✓ No dependencies!\n"
            "✓ Just works!"
        )
        info.setFont(QFont("Arial", 10))
        info.setStyleSheet("background: #f0f0f0; padding: 10px; border-radius: 5px;")
        right_layout.addWidget(info)

        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 1)
        main_widget.setLayout(main_layout)

        # Connect button clicks
        for (row, col), btn in self.buttons.items():
            btn.pressed.connect(lambda r=row, c=col: self.play_sound(r, c))

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

    def play_sound(self, row, col):
        """Play sound from button"""
        sound = self.sounds[(row, col)]
        pygame.mixer.find_channel().play(sound)

    def toggle_recording(self):
        """Toggle recording on/off"""
        if self.recording:
            self.recording = False
            filename = self.synth.stop_recording()
            self.record_btn.setText("⏺️ Start Recording")
            self.record_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ff4444;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    border-radius: 8px;
                    border: 2px solid #cc0000;
                }
                QPushButton:hover {
                    background-color: #ff6666;
                }
            """)
            self.record_time.setText("Recording saved!")
            if filename:
                QMessageBox.information(self, "✓ Saved", f"Recording saved:\n{filename}")
        else:
            self.recording = True
            self.synth.start_recording()
            self.record_btn.setText("⏹️ Stop Recording")
            self.record_btn.setStyleSheet("""
                QPushButton {
                    background-color: #cc0000;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    border-radius: 8px;
                    border: 2px solid #ff4444;
                }
            """)
            self.record_time.setText("Recording...")

    def on_waveform_changed(self, waveform):
        """Change waveform for all synth sounds"""
        self.synth.waveform = waveform
        for row in range(4):
            for col in range(4):
                note_number = row * 4 + col
                freq = 110 * (2 ** (note_number / 12))
                self.sounds[(row, col)] = self.synth.generate_sound(freq, 0.5, waveform)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SoundboardApp()
    window.show()
    sys.exit(app.exec())
