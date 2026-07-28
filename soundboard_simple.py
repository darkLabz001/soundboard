#!/usr/bin/env python3
"""
Professional Music Soundboard - with 30+ sounds and modern UI
"""

import sys
import math
import struct
import random
from datetime import datetime
import wave

try:
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", "pygame"])
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)

try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QGridLayout, QWidget,
                                 QLabel, QVBoxLayout, QHBoxLayout, QGroupBox, QSlider, QMessageBox)
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont, QColor
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", "PyQt6"])
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QGridLayout, QWidget,
                                 QLabel, QVBoxLayout, QHBoxLayout, QGroupBox, QSlider, QMessageBox)
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont, QColor

class ProSynthesizer:
    """Professional synthesizer with 30+ sounds"""

    def __init__(self):
        self.sr = 44100
        self.vol = 0.7
        self.rec_buf = []
        self.is_rec = False

    # DRUMS
    def kick_808(self):
        return self.drum(150, 50, 0.5, 0.08)

    def kick_deep(self):
        return self.drum(100, 40, 0.6, 0.1)

    def snare_crisp(self):
        return self.perc(0.2, 2000, 0.15, 0.05)

    def snare_fat(self):
        return self.perc(0.25, 1500, 0.25, 0.08)

    def hihat_closed(self):
        return self.hihat(0.08)

    def hihat_open(self):
        return self.hihat(0.3)

    def clap(self):
        samples = []
        for i in range(int(self.sr * 0.15)):
            t = i / self.sr
            noise = random.uniform(-1, 1)
            env = 0
            for ht in [0, 0.04]:
                if abs(t - ht) < 0.03:
                    env += math.exp(-abs(t - ht) / 0.02)
            env *= (1 - t / 0.15)
            samples.append(int(noise * env * 0.8 * 32767 * self.vol))
        return self.pack(samples)

    def tom_high(self):
        return self.tom(400, 0.15)

    def tom_mid(self):
        return self.tom(250, 0.15)

    def tom_low(self):
        return self.tom(150, 0.2)

    def cowbell(self):
        samples = []
        for i in range(int(self.sr * 0.2)):
            t = i / self.sr
            sample = math.sin(2 * math.pi * 540 * t) * math.exp(-t / 0.2)
            sample += math.sin(2 * math.pi * 540 * 1.5 * t) * 0.5 * math.exp(-t / 0.2)
            samples.append(int(sample * 32767 * self.vol))
        return self.pack(samples)

    # SYNTHS
    def bass_deep(self, freq):
        return self.synth(freq, 0.6, 'sine')

    def bass_fat(self, freq):
        return self.synth(freq, 0.8, 'square')

    def bass_sub(self, freq):
        return self.synth(freq * 0.5, 0.7, 'sine')

    def lead_bright(self, freq):
        return self.lead(freq, 'square')

    def lead_warm(self, freq):
        return self.lead(freq, 'sine')

    def lead_aggressive(self, freq):
        return self.lead(freq, 'sawtooth')

    def pad_lush(self, freq):
        return self.pad(freq, 1.0, 0.3)

    def pad_ethereal(self, freq):
        return self.pad(freq, 1.2, 0.5)

    def pad_dark(self, freq):
        return self.pad(freq, 0.8, 0.2)

    def pluck(self, freq):
        samples = []
        for i in range(int(self.sr * 0.4)):
            t = i / self.sr
            sample = math.sin(2 * math.pi * freq * t) * math.exp(-t * 8)
            samples.append(int(sample * 0.7 * 32767 * self.vol))
        return self.pack(samples)

    # SYNTH ENGINES
    def drum(self, f_start, f_end, dur, decay):
        samples = []
        for i in range(int(self.sr * dur)):
            t = i / self.sr
            freq = f_end + (f_start - f_end) * math.exp(-t / decay)
            amp = math.exp(-t / decay)
            sample = math.sin(2 * math.pi * freq * t) * amp
            sample += 0.2 * math.sin(2 * math.pi * freq * 2 * t) * amp
            samples.append(int(sample * 0.9 * 32767 * self.vol))
        return self.pack(samples)

    def perc(self, dur, freq, att, dec):
        samples = []
        for i in range(int(self.sr * dur)):
            t = i / self.sr
            noise = random.uniform(-1, 1)
            env = math.exp(-max(0, t - att) / dec) if t > att else (t / att)
            pitch = math.sin(2 * math.pi * freq * t) * 0.5
            sample = (noise * 0.7 + pitch * 0.3) * env
            samples.append(int(sample * 32767 * self.vol))
        return self.pack(samples)

    def hihat(self, dur):
        samples = []
        for i in range(int(self.sr * dur)):
            t = i / self.sr
            noise = random.uniform(-1, 1)
            env = math.exp(-t / (0.08 if dur < 0.1 else 0.2))
            sample = noise * env * (1 - math.exp(-t * 20))
            samples.append(int(sample * 0.6 * 32767 * self.vol))
        return self.pack(samples)

    def tom(self, freq, dur):
        samples = []
        for i in range(int(self.sr * dur)):
            t = i / self.sr
            pitch = freq + freq * 2 * math.exp(-t * 20)
            env = math.exp(-t / 0.1)
            sample = math.sin(2 * math.pi * pitch * t) * env
            samples.append(int(sample * 0.7 * 32767 * self.vol))
        return self.pack(samples)

    def synth(self, freq, dur, wave_type):
        samples = []
        for i in range(int(self.sr * dur)):
            t = i / self.sr
            if wave_type == 'sine':
                wave = math.sin(2 * math.pi * freq * t)
            elif wave_type == 'square':
                wave = 1 if math.sin(2 * math.pi * freq * t) > 0 else -1
            else:
                wave = 2 * (t * freq - math.floor(t * freq + 0.5))

            wave += math.sin(2 * math.pi * freq * 2 * t) * 0.2

            if t < 0.05:
                env = t / 0.05
            else:
                env = max(0, 0.8 - (t - 0.05) * 0.5)

            sample = wave * env * 0.6
            samples.append(int(sample * 32767 * self.vol))
        return self.pack(samples)

    def lead(self, freq, wave_type):
        samples = []
        for i in range(int(self.sr * 0.5)):
            t = i / self.sr
            if wave_type == 'sine':
                wave = math.sin(2 * math.pi * freq * t)
            elif wave_type == 'square':
                wave = 1 if math.sin(2 * math.pi * freq * t) > 0 else -1
            else:
                wave = 2 * (t * freq - math.floor(t * freq + 0.5))

            if t < 0.01:
                env = t / 0.01
            else:
                env = max(0, 0.9 - (t - 0.01) * 1.5)

            sample = wave * env * 0.5
            samples.append(int(sample * 32767 * self.vol))
        return self.pack(samples)

    def pad(self, freq, dur, att):
        samples = []
        for i in range(int(self.sr * dur)):
            t = i / self.sr
            wave = math.sin(2 * math.pi * freq * t) * 0.5
            wave += math.sin(2 * math.pi * freq * 1.5 * t) * 0.3
            wave += math.sin(2 * math.pi * freq * 0.7 * t) * 0.2

            if t < att:
                env = (t / att) ** 0.5
            else:
                env = 0.8

            sample = wave * env * 0.4
            samples.append(int(sample * 32767 * self.vol))
        return self.pack(samples)

    def pack(self, samples):
        return b''.join(struct.pack('<h', max(-32768, min(32767, s))) for s in samples)

    def start_recording(self):
        self.is_rec = True
        self.rec_buf = []

    def stop_recording(self):
        self.is_rec = False
        if self.rec_buf:
            fname = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            rec_bytes = b''.join(struct.pack('<h', max(-32768, min(32767, s))) for s in self.rec_buf)
            try:
                with wave.open(fname, 'wb') as f:
                    f.setnchannels(1)
                    f.setsampwidth(2)
                    f.setframerate(self.sr)
                    f.writeframes(rec_bytes)
                return fname
            except:
                return None
        return None

class ProSoundboardApp(QMainWindow):
    """Professional music production soundboard"""

    def __init__(self):
        super().__init__()
        self.synth = ProSynthesizer()
        self.recording = False
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("🎵 Professional Music Soundboard")
        self.setGeometry(50, 50, 1500, 900)
        self.setStyleSheet("""
            QMainWindow { background-color: #0a0e27; }
            QGroupBox { color: #fff; border: 2px solid #1e3a8a; background-color: #0f172a; }
            QLabel { color: #e0e7ff; }
        """)

        main = QWidget()
        self.setCentralWidget(main)
        layout = QHBoxLayout()

        # DRUMS
        drums_layout = QVBoxLayout()
        drums_grp = QGroupBox("🥁 DRUMS")
        drums_grid = QGridLayout()

        drums_data = [
            ('Kick 808', self.synth.kick_808, '#ff3333'),
            ('Kick Deep', self.synth.kick_deep, '#ff5555'),
            ('Snare', self.synth.snare_crisp, '#ffaa00'),
            ('Snare Fat', self.synth.snare_fat, '#ffbb22'),
            ('Hi-Hat Cls', self.synth.hihat_closed, '#33ff33'),
            ('Hi-Hat Opn', self.synth.hihat_open, '#55ff55'),
            ('Clap', self.synth.clap, '#ff8800'),
            ('Tom High', self.synth.tom_high, '#ffff33'),
            ('Tom Mid', self.synth.tom_mid, '#ffff55'),
            ('Tom Low', self.synth.tom_low, '#ffff77'),
            ('Cowbell', self.synth.cowbell, '#00ffff'),
        ]

        for idx, (name, func, color) in enumerate(drums_data):
            btn = self.btn(name, color, 70)
            btn.pressed.connect(lambda f=func: self.play(f()))
            drums_grid.addWidget(btn, idx // 4, idx % 4)

        drums_grp.setLayout(drums_grid)
        drums_layout.addWidget(drums_grp)
        drums_layout.addStretch()

        # BASS
        bass_layout = QVBoxLayout()
        bass_grp = QGroupBox("🎸 BASS")
        bass_grid = QGridLayout()

        bass_types = [('Deep', self.synth.bass_deep), ('Fat', self.synth.bass_fat), ('Sub', self.synth.bass_sub)]
        notes = [55, 82.41, 110, 146.83, 195.99, 246.94, 329.63]
        note_names = ['A1', 'E2', 'A2', 'D3', 'B3', 'B3', 'E4']

        row = 0
        for bname, bfunc in bass_types:
            for col, (freq, note) in enumerate(zip(notes, note_names)):
                btn = self.btn(f"{note}\n{bname}", '#0088ff', 60)
                btn.pressed.connect(lambda f=freq, bf=bfunc: self.play(bf(f)))
                bass_grid.addWidget(btn, row, col)
            row += 1

        bass_grp.setLayout(bass_grid)
        bass_layout.addWidget(bass_grp)
        bass_layout.addStretch()

        # LEADS
        lead_layout = QVBoxLayout()
        lead_grp = QGroupBox("🎹 LEADS")
        lead_grid = QGridLayout()

        lead_types = [('Bright', self.synth.lead_bright), ('Warm', self.synth.lead_warm), ('Aggro', self.synth.lead_aggressive)]
        row = 0
        for lname, lfunc in lead_types:
            for col, (freq, note) in enumerate(zip(notes, note_names)):
                btn = self.btn(f"{note}\n{lname}", '#ff00ff', 60)
                btn.pressed.connect(lambda f=freq, lf=lfunc: self.play(lf(f)))
                lead_grid.addWidget(btn, row, col)
            row += 1

        lead_grp.setLayout(lead_grid)
        lead_layout.addWidget(lead_grp)

        # PADS
        pad_grp = QGroupBox("🌊 PADS")
        pad_grid = QGridLayout()

        pad_types = [('Lush', self.synth.pad_lush), ('Ethreal', self.synth.pad_ethereal), ('Dark', self.synth.pad_dark), ('Pluck', self.synth.pluck)]
        row = 0
        for pname, pfunc in pad_types:
            for col, (freq, note) in enumerate(zip(notes[:4], note_names[:4])):
                btn = self.btn(f"{note}\n{pname}", '#00ffaa', 55)
                btn.pressed.connect(lambda f=freq, pf=pfunc: self.play(pf(f)))
                pad_grid.addWidget(btn, row, col)
            row += 1

        pad_grp.setLayout(pad_grid)
        lead_layout.addWidget(pad_grp)
        lead_layout.addStretch()

        # CONTROLS
        ctrl_layout = QVBoxLayout()

        rec_grp = QGroupBox("🎙️ RECORDING")
        rec_l = QVBoxLayout()
        self.rec_btn = self.btn("⏺️ START", '#ff4444', 50)
        self.rec_btn.pressed.connect(self.toggle_rec)
        rec_l.addWidget(self.rec_btn)
        self.rec_lbl = QLabel("Ready")
        self.rec_lbl.setStyleSheet("color: #888; font-size: 10px;")
        rec_l.addWidget(self.rec_lbl)
        rec_grp.setLayout(rec_l)
        ctrl_layout.addWidget(rec_grp)

        vol_grp = QGroupBox("🔊 VOLUME")
        vol_l = QVBoxLayout()
        vol_slider = QSlider(Qt.Orientation.Vertical)
        vol_slider.setMinimum(0)
        vol_slider.setMaximum(100)
        vol_slider.setValue(70)
        vol_slider.sliderMoved.connect(lambda v: setattr(self.synth, 'vol', v / 100))
        vol_l.addWidget(vol_slider)
        vol_grp.setLayout(vol_l)
        ctrl_layout.addWidget(vol_grp)

        info = QLabel("🎵 30+ SOUNDS\n\n✓ 11 Drums\n✓ 9 Bass Synths\n✓ 9 Leads\n✓ 8 Pads\n\nClick or press!")
        info.setStyleSheet("color: #aaa; font-size: 10px;")
        ctrl_layout.addWidget(info)
        ctrl_layout.addStretch()

        layout.addLayout(drums_layout, 1)
        layout.addLayout(bass_layout, 1)
        layout.addLayout(lead_layout, 1)
        layout.addLayout(ctrl_layout, 0)

        main.setLayout(layout)

    def btn(self, text, color, size):
        b = QPushButton(text)
        b.setMinimumSize(size, size)
        b.setFont(QFont("Arial", 7, QFont.Weight.Bold))
        b.setStyleSheet(f"""
            QPushButton {{
                background-color: {color}; color: white;
                border: 1px solid #000; border-radius: 3px;
            }}
            QPushButton:pressed {{ background-color: {QColor(color).lighter(150).name()}; }}
        """)
        return b

    def play(self, audio):
        snd = pygame.mixer.Sound(buffer=audio)
        pygame.mixer.find_channel().play(snd)

        if self.synth.is_rec:
            samples = [int.from_bytes(audio[i:i+2], 'little', signed=True) for i in range(0, len(audio), 2)]
            self.synth.rec_buf.extend(samples)

    def toggle_rec(self):
        if self.recording:
            self.recording = False
            fname = self.synth.stop_recording()
            self.rec_btn.setText("⏺️ START")
            if fname:
                self.rec_lbl.setText(f"✓ {fname}")
                QMessageBox.information(self, "Saved", f"Recording: {fname}")
        else:
            self.recording = True
            self.rec_btn.setText("⏹️ STOP")
            self.synth.start_recording()
            self.rec_lbl.setText("Recording...")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProSoundboardApp()
    window.show()
    sys.exit(app.exec())
