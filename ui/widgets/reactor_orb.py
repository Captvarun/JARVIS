import math
import random
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient
from PySide6.QtWidgets import QWidget

class ReactorOrbWidget(QWidget):
    """
    Advanced Concentric Vector AI Reactor Core.
    Implements 8 layered visual elements and dynamic state-based visual behaviors:
    - IDLE: Soft cyan, breathing pulse, slow ring rotation.
    - LISTENING: Bright cyan, audio-reactive core expansion.
    - THINKING: Cyber blue, rapid counter-rotation with radar reticle sweep.
    - SPEAKING: Amber (#ffb455), expanding particle ring emission.
    - ERROR: Restrained red (#ef4444), warning pulse & jitter.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(240, 240)
        
        self.current_state = "IDLE"
        self.angle = 0.0
        self.pulse = 0.0
        self.pulse_dir = 1.0
        self.audio_level = 0.0

        # Orbital Particles setup
        self.particles = []
        for _ in range(16):
            self.particles.append({
                "angle": random.uniform(0, 360),
                "dist_factor": random.uniform(0.35, 0.75),
                "size": random.uniform(2.0, 4.0),
                "speed": random.uniform(0.5, 1.5)
            })

        # State Color Map
        self.state_colors = {
            "IDLE": QColor(79, 208, 255),      # Soft Cyan #4fd0ff
            "LISTENING": QColor(143, 227, 255), # Bright Cyan #8fe3ff
            "THINKING": QColor(56, 189, 248),  # Cyber Blue #38bdf8
            "SPEAKING": QColor(255, 180, 85),  # Amber #ffb455 (RESERVED FOR SPEAKING)
            "ERROR": QColor(239, 68, 68)       # Restrained Red #ef4444
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
            rot_speed = 3.5
        elif self.current_state == "SPEAKING":
            rot_speed = 2.0
        else:
            rot_speed = 1.0

        self.angle = (self.angle + rot_speed) % 360.0

        # Pulse Frequency
        pulse_speed = 0.03 if self.current_state == "IDLE" else 0.06
        self.pulse += pulse_speed * self.pulse_dir
        if self.pulse >= 1.0:
            self.pulse = 1.0
            self.pulse_dir = -1.0
        elif self.pulse <= 0.0:
            self.pulse = 0.0
            self.pulse_dir = 1.0

        # Particles Animation
        for p in self.particles:
            p["angle"] = (p["angle"] + p["speed"]) % 360.0
            if self.current_state == "SPEAKING":
                # Scale outward during speech
                p["dist_factor"] += 0.005
                if p["dist_factor"] > 0.95:
                    p["dist_factor"] = 0.35
            elif self.current_state == "LISTENING":
                # Inward drift
                p["dist_factor"] -= 0.005
                if p["dist_factor"] < 0.30:
                    p["dist_factor"] = 0.80

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

        # 1. Atmospheric Radial Bloom Aura
        radial_grad = QRadialGradient(0, 0, radius * 1.1)
        bloom_alpha = int(40 + 30 * self.pulse)
        radial_grad.setColorAt(0.0, QColor(color.red(), color.green(), color.blue(), bloom_alpha))
        radial_grad.setColorAt(0.6, QColor(color.red(), color.green(), color.blue(), int(bloom_alpha * 0.3)))
        radial_grad.setColorAt(1.0, QColor(3, 5, 9, 0))
        painter.setBrush(radial_grad)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(-radius * 1.1, -radius * 1.1, radius * 2.2, radius * 2.2))

        # 2. Outer Reference Dotted Ring
        painter.save()
        dot_pen = QPen(QColor(color.red(), color.green(), color.blue(), 100), 1.5, Qt.DotLine)
        painter.setPen(dot_pen)
        painter.drawEllipse(QRectF(-radius * 0.9, -radius * 0.9, radius * 1.8, radius * 1.8))
        painter.restore()

        # 3. Rotating Outer Dashed Ring
        painter.save()
        painter.rotate(self.angle)
        dash_pen = QPen(QColor(color.red(), color.green(), color.blue(), 200), 2.0, Qt.DashLine)
        painter.setPen(dash_pen)
        painter.drawEllipse(QRectF(-radius * 0.8, -radius * 0.8, radius * 1.6, radius * 1.6))
        painter.restore()

        # 4. Rotating Counter Reticle Quadrant Crosshair
        painter.save()
        painter.rotate(-self.angle * 1.4)
        crosshair_pen = QPen(QColor(color.red(), color.green(), color.blue(), 160), 1.2)
        painter.setPen(crosshair_pen)
        r_sub = radius * 0.65
        painter.drawLine(QPointF(-r_sub, 0), QPointF(r_sub, 0))
        painter.drawLine(QPointF(0, -r_sub), QPointF(0, r_sub))
        painter.drawEllipse(QRectF(-r_sub, -r_sub, r_sub * 2.0, r_sub * 2.0))
        painter.restore()

        # 5. Orbital Particles Ring Layer
        painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 220)))
        painter.setPen(Qt.NoPen)
        for p in self.particles:
            rad = math.radians(p["angle"])
            dist = radius * p["dist_factor"]
            px = dist * math.cos(rad)
            py = dist * math.sin(rad)
            sz = p["size"]
            painter.drawEllipse(QRectF(px - sz/2, py - sz/2, sz, sz))

        # 6. Inner Energy Ring
        inner_r = radius * (0.4 + 0.05 * self.pulse)
        if self.current_state == "LISTENING":
            inner_r += radius * 0.1 * self.audio_level

        inner_pen = QPen(QColor(255, 255, 255, 220), 2.0)
        painter.setPen(inner_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QRectF(-inner_r, -inner_r, inner_r * 2.0, inner_r * 2.0))

        # 7. Central Glowing Core
        core_r = inner_r * 0.6
        core_grad = QRadialGradient(0, 0, core_r)
        core_grad.setColorAt(0.0, QColor(255, 255, 255, 240))
        core_grad.setColorAt(0.5, QColor(color.red(), color.green(), color.blue(), 210))
        core_grad.setColorAt(1.0, QColor(color.red(), color.green(), color.blue(), 0))
        painter.setBrush(core_grad)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(-core_r, -core_r, core_r * 2.0, core_r * 2.0))
