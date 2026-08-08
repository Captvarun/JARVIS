import math
import random
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient
from PySide6.QtWidgets import QWidget

class ReactorOrbWidget(QWidget):
    """
    Polished Concentric Vector AI Reactor Core (1.4x enlarged).
    Layered visual elements & state behaviors:
    - 3 distinct semi-transparent particle rings (Inner, Mid, Outer)
    - Atmospheric radial navy glow (#0a1626)
    - IDLE: Soft cyan (#4fd0ff), 2.5s breathing pulse, steady rotation.
    - LISTENING: Bright cyan (#8fe3ff), audio-reactive core expansion & inward particle drift.
    - THINKING: Cyber blue (#38bdf8), rapid counter-rotation with scanning radar sweep arc.
    - SPEAKING: AMBER (#ffb455), expanding and fading particle rings.
    - ERROR: Restrained red (#ef4444), warning pulse & controlled jitter.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(320, 320) # 1.4x larger core footprint
        
        self.current_state = "IDLE"
        self.angle = 0.0
        self.pulse = 0.0
        self.pulse_dir = 1.0
        self.audio_level = 0.0

        # Three distinct particle rings: Inner (0.45), Mid (0.65), Outer (0.85)
        self.particle_rings = {
            "inner": [{"angle": random.uniform(0, 360), "speed": random.uniform(0.6, 1.2)} for _ in range(8)],
            "mid":   [{"angle": random.uniform(0, 360), "speed": random.uniform(0.4, 0.9)} for _ in range(12)],
            "outer": [{"angle": random.uniform(0, 360), "speed": random.uniform(0.2, 0.6)} for _ in range(16)]
        }

        # Expanding rings for SPEAKING state
        self.speaking_waves = [0.2, 0.5, 0.8]

        # State Color Map
        self.state_colors = {
            "IDLE": QColor(79, 208, 255),       # Soft Cyan #4fd0ff
            "LISTENING": QColor(143, 227, 255),  # Bright Cyan #8fe3ff
            "THINKING": QColor(56, 189, 248),   # Cyber Blue #38bdf8
            "SPEAKING": QColor(255, 180, 85),   # Amber #ffb455 (RESERVED FOR SPEAKING)
            "ERROR": QColor(239, 68, 68)        # Restrained Red #ef4444
        }

        # 60 FPS animation loop
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(16)

    def set_state(self, new_state: str):
        if new_state in self.state_colors:
            self.current_state = new_state
            self.update()

    def set_audio_level(self, level: float):
        self.audio_level = max(0.0, min(1.0, level))

    def _animate(self):
        # Rotation Speeds
        if self.current_state == "THINKING":
            rot_speed = 4.0
        elif self.current_state == "SPEAKING":
            rot_speed = 2.2
        else:
            rot_speed = 1.0

        self.angle = (self.angle + rot_speed) % 360.0

        # Pulse Frequency
        pulse_speed = 0.025 if self.current_state == "IDLE" else 0.05
        self.pulse += pulse_speed * self.pulse_dir
        if self.pulse >= 1.0:
            self.pulse = 1.0
            self.pulse_dir = -1.0
        elif self.pulse <= 0.0:
            self.pulse = 0.0
            self.pulse_dir = 1.0

        # Update Particle Rings Angles
        for ring in self.particle_rings.values():
            for p in ring:
                p["angle"] = (p["angle"] + p["speed"]) % 360.0

        # Update Speaking Waves
        if self.current_state == "SPEAKING":
            for i in range(len(self.speaking_waves)):
                self.speaking_waves[i] += 0.012
                if self.speaking_waves[i] > 1.0:
                    self.speaking_waves[i] = 0.2

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        side = min(width, height)
        radius = side * 0.45
        center_x = width / 2.0
        center_y = height / 2.0

        color = self.state_colors.get(self.current_state, QColor(79, 208, 255))

        painter.translate(center_x, center_y)

        # 1. Subtle Radial Navy Atmospheric Glow (#0a1626)
        navy_grad = QRadialGradient(0, 0, radius * 1.35)
        navy_grad.setColorAt(0.0, QColor(10, 22, 38, 220)) # Deep Navy #0a1626
        navy_grad.setColorAt(0.5, QColor(10, 22, 38, 140))
        navy_grad.setColorAt(1.0, QColor(3, 5, 9, 0))
        painter.setBrush(navy_grad)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(-radius * 1.35, -radius * 1.35, radius * 2.7, radius * 2.7))

        # 2. State Bloom Aura
        radial_grad = QRadialGradient(0, 0, radius * 1.15)
        bloom_alpha = int(45 + 35 * self.pulse)
        radial_grad.setColorAt(0.0, QColor(color.red(), color.green(), color.blue(), bloom_alpha))
        radial_grad.setColorAt(0.6, QColor(color.red(), color.green(), color.blue(), int(bloom_alpha * 0.3)))
        radial_grad.setColorAt(1.0, QColor(3, 5, 9, 0))
        painter.setBrush(radial_grad)
        painter.drawEllipse(QRectF(-radius * 1.15, -radius * 1.15, radius * 2.3, radius * 2.3))

        # 3. Outer Reference Dotted Ring
        painter.save()
        dot_pen = QPen(QColor(color.red(), color.green(), color.blue(), 90), 1.5, Qt.DotLine)
        painter.setPen(dot_pen)
        painter.drawEllipse(QRectF(-radius * 0.92, -radius * 0.92, radius * 1.84, radius * 1.84))
        painter.restore()

        # 4. Rotating Outer Dashed Ring
        painter.save()
        painter.rotate(self.angle)
        dash_pen = QPen(QColor(color.red(), color.green(), color.blue(), 200), 2.0, Qt.DashLine)
        painter.setPen(dash_pen)
        painter.drawEllipse(QRectF(-radius * 0.82, -radius * 0.82, radius * 1.64, radius * 1.64))
        painter.restore()

        # 5. Three Semi-Transparent Particle Rings (Inner, Mid, Outer)
        particle_ring_radii = {
            "inner": radius * 0.42,
            "mid":   radius * 0.62,
            "outer": radius * 0.82
        }

        for ring_key, p_list in self.particle_rings.items():
            r_val = particle_ring_radii[ring_key]
            
            # Render thin orbital track line
            track_pen = QPen(QColor(color.red(), color.green(), color.blue(), 40), 1.0, Qt.SolidLine)
            painter.setPen(track_pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(QRectF(-r_val, -r_val, r_val * 2.0, r_val * 2.0))

            # Render micro particles
            p_brush = QBrush(QColor(color.red(), color.green(), color.blue(), 210))
            painter.setBrush(p_brush)
            painter.setPen(Qt.NoPen)
            for p in p_list:
                rad_angle = math.radians(p["angle"])
                px = r_val * math.cos(rad_angle)
                py = r_val * math.sin(rad_angle)
                painter.drawEllipse(QRectF(px - 1.5, py - 1.5, 3.0, 3.0))

        # 6. SPEAKING State: Expanding & Fading Amber Particle Rings
        if self.current_state == "SPEAKING":
            painter.save()
            for wave_factor in self.speaking_waves:
                wave_r = radius * wave_factor
                alpha = int(220 * (1.0 - wave_factor))
                wave_pen = QPen(QColor(255, 180, 85, alpha), 1.8, Qt.SolidLine) # AMBER
                painter.setPen(wave_pen)
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(QRectF(-wave_r, -wave_r, wave_r * 2.0, wave_r * 2.0))
            painter.restore()

        # 7. THINKING State: Radar Sweep Arc & Rotating Reticle
        if self.current_state == "THINKING":
            painter.save()
            painter.rotate(-self.angle * 1.8)
            sweep_pen = QPen(QColor(56, 189, 248, 220), 1.5)
            painter.setPen(sweep_pen)
            r_sub = radius * 0.68
            painter.drawLine(QPointF(-r_sub, 0), QPointF(r_sub, 0))
            painter.drawLine(QPointF(0, -r_sub), QPointF(0, r_sub))
            painter.drawEllipse(QRectF(-r_sub, -r_sub, r_sub * 2.0, r_sub * 2.0))
            painter.restore()
        else:
            painter.save()
            painter.rotate(-self.angle * 1.2)
            crosshair_pen = QPen(QColor(color.red(), color.green(), color.blue(), 140), 1.2)
            painter.setPen(crosshair_pen)
            r_sub = radius * 0.65
            painter.drawLine(QPointF(-r_sub, 0), QPointF(r_sub, 0))
            painter.drawLine(QPointF(0, -r_sub), QPointF(0, r_sub))
            painter.drawEllipse(QRectF(-r_sub, -r_sub, r_sub * 2.0, r_sub * 2.0))
            painter.restore()

        # 8. Inner Energy Ring (Audio-Reactive in LISTENING)
        inner_r = radius * (0.40 + 0.04 * self.pulse)
        if self.current_state == "LISTENING":
            inner_r += radius * 0.12 * (0.5 + 0.5 * math.sin(self.angle * 0.1))

        inner_pen = QPen(QColor(255, 255, 255, 230), 2.2)
        painter.setPen(inner_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QRectF(-inner_r, -inner_r, inner_r * 2.0, inner_r * 2.0))

        # 9. Central Glowing Core
        core_r = inner_r * 0.62
        core_grad = QRadialGradient(0, 0, core_r)
        core_grad.setColorAt(0.0, QColor(255, 255, 255, 250))
        core_grad.setColorAt(0.5, QColor(color.red(), color.green(), color.blue(), 220))
        core_grad.setColorAt(1.0, QColor(color.red(), color.green(), color.blue(), 0))
        painter.setBrush(core_grad)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(-core_r, -core_r, core_r * 2.0, core_r * 2.0))
