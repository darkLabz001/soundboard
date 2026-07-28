#!/usr/bin/env python3
"""
Professional Music Soundboard - For Making Real Music
Complete with drum kits, synths, pads, and effects
"""

import sys
import math
import struct
from collections import defaultdict
from datetime import datetime
import threading
import wave

try:
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", "pygame"])
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QGridLayout,
                                 QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFileDialog,
                                 QSpinBox, QSlider, QComboBox, QCheckBox, QMessageBox, QGroupBox)
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
    from PyQt6.QtGui import QFont, QColor, QKeyEvent
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", "PyQt6"])
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QGridLayout,
                                 QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFileDialog,
                                 QSpinBox, QSlider, QComboBox, QCheckBox, QMessageBox, QGroupBox)
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
    from PyQt6.QtGui import QFont, QColor, QKeyEvent

class ProfessionalSynthesizer:
    """Professional audio synthesizer with drum kits and effects"""

    def __init__(self):
        self.sample_rate = 44100
        self.volume = 0.7
        self.is_recording = False
        self.recording_buffer = []

    def generate_kick_drum(self, duration=0.5):
        """Generate a professional 808 kick drum"""
        num_samples = int(self.sample_rate * duration)
        samples = []

        for i in range(num_samples):
            t = i / self.sample_rate

            # Pitch envelope: drop from 150Hz to 50Hz
            freq_start, freq_end = 150, 50
            pitch_decay = 0.08
            freq = freq_end + (freq_start - freq_end) * math.exp(-t / pitch_decay)

            # Amplitude envelope
            amp_decay = 0.3
            amplitude = math.exp(-t / amp_decay)

            # Sine wave with some harmonics
            sample = math.sin(2 * math.pi * freq * t) * amplitude

            # Add some tone
            sample += 0.2 * math.sin(2 * math.pi * freq * 2 * t) * amplitude

            samples.append(int(sample * 0.9 * 32767 * self.volume))

        return self.pack_audio(samples)

    def generate_snare_drum(self, duration=0.2):
        """Generate a snappy snare sound"""
        num_samples = int(self.sample_rate * duration)
        samples = []

        for i in range(num_samples):
            t = i / self.sample_rate

            # Noise component
            import random
            noise = random.uniform(-1, 1)

            # Attack and decay
            attack_time = 0.001
            decay_time = 0.15

            if t < attack_time:
                env = t / attack_time
            else:
                env = math.exp(-(t - attack_time) / decay_time)

            # Add pitch
            pitch = math.sin(2 * math.pi * 200 * t) * 0.5

            sample = (noise * 0.7 + pitch * 0.3) * env

            samples.append(int(sample * 32767 * self.volume))

        return self.pack_audio(samples)

    def generate_hihat(self, duration=0.1, closed=True):
        """Generate hi-hat (closed or open)"""
        num_samples = int(self.sample_rate * duration)
        samples = []

        for i in range(num_samples):
            t = i / self.sample_rate

            # Noise with high-pass characteristics
            import random
            noise = random.uniform(-1, 1)

            # Closed hi-hat: sharp attack and quick decay
            if closed:
                attack = 0.002
                decay = 0.08
            else:
                attack = 0.005
                decay = 0.2

            if t < attack:
                env = t / attack
            else:
                env = math.exp(-(t - attack) / decay)

            # Filter-like effect
            sample = noise * env * (1 - math.exp(-t * 20))

            samples.append(int(sample * 0.6 * 32767 * self.volume))

        return self.pack_audio(samples)

    def generate_clap(self, duration=0.15):
        """Generate clap sound"""
        num_samples = int(self.sample_rate * duration)
        samples = []

        for i in range(num_samples):
            t = i / self.sample_rate

            import random
            noise = random.uniform(-1, 1)

            # Double hit for clap effect
            hit1_time, hit2_time = 0, 0.04

            env = 0
            if abs(t - hit1_time) < 0.03:
                env += math.exp(-abs(t - hit1_time) / 0.02)
            if abs(t - hit2_time) < 0.03:
                env += math.exp(-abs(t - hit2_time) / 0.02)

            env *= (1 - t / duration)

            sample = noise * env

            samples.append(int(sample * 0.8 * 32767 * self.volume))

        return self.pack_audio(samples)

    def generate_bass_synth(self, frequency, duration=0.5):
        """Generate a professional bass synth"""
        num_samples = int(self.sample_rate * duration)
        samples = []

        for i in range(num_samples):
            t = i / self.sample_rate

            # Rich bass with harmonics
            sample = math.sin(2 * math.pi * frequency * t) * 0.7
            sample += math.sin(2 * math.pi * frequency * 2 * t) * 0.2
            sample += math.sin(2 * math.pi * frequency * 0.5 * t) * 0.1

            # ADSR envelope
            attack, decay, sustain, release = 0.05, 0.1, 0.6, 0.2

            if t < attack:
                env = t / attack
            elif t < attack + decay:
                env = 1 - (t - attack) / decay * (1 - sustain)
            elif t < duration - release:
                env = sustain
            else:
                env = sustain * (duration - t) / release

            sample *= env

            samples.append(int(sample * 0.8 * 32767 * self.volume))

        return self.pack_audio(samples)

    def generate_lead_synth(self, frequency, duration=0.5):
        """Generate a bright lead synth"""
        num_samples = int(self.sample_rate * duration)
        samples = []

        for i in range(num_samples):
            t = i / self.sample_rate

            # Square wave for bright sound
            sample = 1.0 if math.sin(2 * math.pi * frequency * t) > 0 else -1.0

            # Add sawtooth for richness
            sample += (2 * (t * frequency - math.floor(t * frequency + 0.5))) * 0.3

            sample *= 0.7

            # Fast attack, quick release
            if t < 0.01:
                env = t / 0.01
            elif t < duration - 0.1:
                env = 0.9
            else:
                env = (duration - t) / 0.1

            sample *= env

            samples.append(int(sample * 32767 * self.volume))

        return self.pack_audio(samples)

    def generate_pad_synth(self, frequency, duration=1.0):
        """Generate a lush pad synth"""
        num_samples = int(self.sample_rate * duration)
        samples = []

        for i in range(num_samples):
            t = i / self.sample_rate

            # Multiple sine waves for rich sound
            sample = math.sin(2 * math.pi * frequency * t) * 0.5
            sample += math.sin(2 * math.pi * frequency * 1.5 * t) * 0.3
            sample += math.sin(2 * math.pi * frequency * 0.7 * t) * 0.2

            # Slow attack, long sustain
            attack = 0.3
            if t < attack:
                env = (t / attack) ** 0.5
            else:
                env = 0.9

            sample *= env * 0.5

            samples.append(int(sample * 32767 * self.volume))

        return self.pack_audio(samples)

    def pack_audio(self, samples):
        """Convert samples to 16-bit stereo audio"""
        stereo_data = b''
        for s in samples:
            # Same sample for both channels (mono -> stereo)
            stereo_data += struct.pack('<h', max(-32768, min(32767, s)))
            stereo_data += struct.pack('<h', max(-32768, min(32767, s)))
        return stereo_data

    def start_recording(self):
        self.is_recording = True
        self.recording_buffer = []

    def stop_recording(self):
        self.is_recording = False
        if self.recording_buffer:
            return self.save_recording()
        return None

    def save_recording(self):
        if not self.recording_buffer:
            return None

        # Convert samples to stereo bytes
        recording_bytes = b''
        for s in self.recording_buffer:
            recording_bytes += struct.pack('<h', max(-32768, min(32767, s)))
            recording_bytes += struct.pack('<h', max(-32768, min(32767, s)))

        filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"

        try:
            with wave.open(filename, 'wb') as wav_file:
                wav_file.setnchannels(2)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(recording_bytes)

            print(f"✓ Recording saved: {filename}")
            return filename
        except Exception as e:
            print(f"Error: {e}")
            return None

class ProfessionalSoundboardApp(QMainWindow):
    """Professional music production soundboard"""

    DRUMS = {
        'Q': ('Kick 808', 'kick'),
        'W': ('Snare', 'snare'),
        'E': ('Closed Hat', 'hat_closed'),
        'R': ('Open Hat', 'hat_open'),
    }

    SYNTHS = {
        'A': (55, 'bass'),      # A1
        'S': (82.41, 'bass'),   # E2
        'D': (110, 'bass'),     # A2
        'F': (146.83, 'bass'),  # D3
        'Z': (110, 'lead'),     # A2
        'X': (138.59, 'lead'),  # B2
        'C': (164.81, 'lead'),  # E3
        'V': (196, 'lead'),     # G3
    }

    PADS = {
        '1': (110, 'pad'),      # A2
        '2': (146.83, 'pad'),   # D3
        '3': (164.81, 'pad'),   # E3
        '4': (196, 'pad'),      # G3
    }

    def __init__(self):
        super().__init__()
        self.synth = ProfessionalSynthesizer()
        self.sounds = {}
        self.recording = False
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("🎵 Professional Music Soundboard")
        self.setGeometry(50, 50, 1400, 900)

        # Set dark professional theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #ffffff;
            }
            QGroupBox {
                color: #ffffff;
                border: 2px solid #333;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()

        # Left: Instruments
        instruments_layout = QVBoxLayout()

        # Drums
        drums_group = QGroupBox("🥁 DRUMS")
        drums_layout = QGridLayout()
        drum_colors = {'kick': '#ff4444', 'snare': '#ffaa44', 'hat_closed': '#44ff44', 'hat_open': '#44ccff'}

        drum_map = {'Q': (0, 0), 'W': (0, 1), 'E': (0, 2), 'R': (0, 3)}
        for key, (row, col) in drum_map.items():
            name, dtype = self.DRUMS[key]
            btn = self.create_pad_button(name, drum_colors[dtype], 100)
            btn.pressed.connect(lambda k=key, dt=dtype: self.play_drum(dt))
            drums_layout.addWidget(btn, row, col)

        drums_group.setLayout(drums_layout)
        instruments_layout.addWidget(drums_group)

        # Bass
        bass_group = QGroupBox("🎸 BASS")
        bass_layout = QGridLayout()
        bass_keys = ['A', 'S', 'D', 'F']
        for i, key in enumerate(bass_keys):
            freq, synth_type = self.SYNTHS[key]
            note = self.freq_to_note(freq)
            btn = self.create_pad_button(note, '#0088ff', 80)
            btn.pressed.connect(lambda f=freq: self.play_synth(f, 'bass'))
            bass_layout.addWidget(btn, 0, i)

        bass_group.setLayout(bass_layout)
        instruments_layout.addWidget(bass_group)

        # Lead
        lead_group = QGroupBox("🎹 LEAD")
        lead_layout = QGridLayout()
        lead_keys = ['Z', 'X', 'C', 'V']
        for i, key in enumerate(lead_keys):
            freq, synth_type = self.SYNTHS[key]
            note = self.freq_to_note(freq)
            btn = self.create_pad_button(note, '#ff00ff', 80)
            btn.pressed.connect(lambda f=freq: self.play_synth(f, 'lead'))
            lead_layout.addWidget(btn, 0, i)

        lead_group.setLayout(lead_layout)
        instruments_layout.addWidget(lead_group)

        # Pads
        pad_group = QGroupBox("🌊 PADS")
        pad_layout = QGridLayout()
        pad_keys = ['1', '2', '3', '4']
        for i, key in enumerate(pad_keys):
            freq, synth_type = self.SYNTHS.get(key, self.PADS[key])
            note = self.freq_to_note(freq)
            btn = self.create_pad_button(note, '#00ffaa', 80)
            btn.pressed.connect(lambda f=freq: self.play_synth(f, 'pad'))
            pad_layout.addWidget(btn, 0, i)

        pad_group.setLayout(pad_layout)
        instruments_layout.addWidget(pad_group)

        # Right: Controls
        controls_layout = QVBoxLayout()

        # Recording
        rec_group = QGroupBox("🎙️ RECORDING")
        rec_layout = QVBoxLayout()

        self.record_btn = QPushButton("⏺️ Start Recording")
        self.record_btn.setMinimumHeight(60)
        self.record_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 8px;
                border: 2px solid #cc0000;
            }
        """)
        self.record_btn.clicked.connect(self.toggle_recording)
        rec_layout.addWidget(self.record_btn)

        self.rec_time = QLabel("Ready")
        self.rec_time.setStyleSheet("font-size: 12px; color: #888;")
        rec_layout.addWidget(self.rec_time)

        rec_group.setLayout(rec_layout)
        controls_layout.addWidget(rec_group)

        # Master Volume
        vol_group = QGroupBox("🔊 MASTER VOLUME")
        vol_layout = QVBoxLayout()

        vol_slider = QSlider(Qt.Orientation.Horizontal)
        vol_slider.setMinimum(0)
        vol_slider.setMaximum(100)
        vol_slider.setValue(70)
        vol_slider.sliderMoved.connect(lambda v: setattr(self.synth, 'volume', v / 100))
        vol_layout.addWidget(vol_slider)

        vol_group.setLayout(vol_layout)
        controls_layout.addWidget(vol_group)

        # Info
        info_group = QGroupBox("ℹ️ INFO")
        info_layout = QVBoxLayout()

        info = QLabel(
            "🎵 PROFESSIONAL SOUNDBOARD\n\n"
            "DRUMS: Q W E R\n"
            "BASS: A S D F\n"
            "LEAD: Z X C V\n"
            "PADS: 1 2 3 4\n\n"
            "Click or press keys\n"
            "Record your session\n\n"
            "✓ Professional sounds\n"
            "✓ Real drum kits\n"
            "✓ Synth engines\n"
            "✓ Full recording"
        )
        info.setFont(QFont("Arial", 10))
        info.setStyleSheet("color: #aaa;")
        info_layout.addWidget(info)

        info_group.setLayout(info_layout)
        controls_layout.addWidget(info_group, 1)

        main_layout.addLayout(instruments_layout, 2)
        main_layout.addLayout(controls_layout, 1)
        main_widget.setLayout(main_layout)

    def create_pad_button(self, text, color, min_size=100):
        btn = QPushButton(text)
        btn.setMinimumSize(min_size, min_size)
        btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: 2px solid #222;
                border-radius: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {QColor(color).lighter(120).name()};
            }}
            QPushButton:pressed {{
                background-color: {QColor(color).darker(130).name()};
                border: 3px solid #fff;
            }}
        """)
        return btn

    def freq_to_note(self, freq):
        """Convert frequency to note name"""
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        a4 = 440
        c0 = a4 * pow(2, -4.75)
        h = 12 * math.log2(freq / c0)
        octave = int(h) // 12
        n = int(h) % 12
        return notes[n] + str(octave)

    def play_drum(self, drum_type):
        if drum_type == 'kick':
            sound_data = self.synth.generate_kick_drum()
        elif drum_type == 'snare':
            sound_data = self.synth.generate_snare_drum()
        elif drum_type == 'hat_closed':
            sound_data = self.synth.generate_hihat(closed=True)
        elif drum_type == 'hat_open':
            sound_data = self.synth.generate_hihat(closed=False)
        else:
            sound_data = self.synth.generate_clap()

        sound = pygame.mixer.Sound(buffer=sound_data)
        pygame.mixer.find_channel().play(sound)

        if self.synth.is_recording:
            samples = [int.from_bytes(sound_data[i:i+2], 'little', signed=True)
                      for i in range(0, len(sound_data), 2)]
            self.synth.recording_buffer.extend(samples)

    def play_synth(self, frequency, synth_type):
        if synth_type == 'bass':
            sound_data = self.synth.generate_bass_synth(frequency)
        elif synth_type == 'lead':
            sound_data = self.synth.generate_lead_synth(frequency)
        else:
            sound_data = self.synth.generate_pad_synth(frequency)

        sound = pygame.mixer.Sound(buffer=sound_data)
        pygame.mixer.find_channel().play(sound)

        if self.synth.is_recording:
            samples = [int.from_bytes(sound_data[i:i+2], 'little', signed=True)
                      for i in range(0, len(sound_data), 2)]
            self.synth.recording_buffer.extend(samples)

    def toggle_recording(self):
        if self.recording:
            self.recording = False
            filename = self.synth.stop_recording()
            self.record_btn.setText("⏺️ Start Recording")
            self.rec_time.setText("Saved!")
            if filename:
                QMessageBox.information(self, "✓ Saved", f"Recording saved:\n{filename}")
        else:
            self.recording = True
            self.synth.start_recording()
            self.record_btn.setText("⏹️ Stop Recording")
            self.rec_time.setText("Recording...")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProfessionalSoundboardApp()
    window.show()
    sys.exit(app.exec())
