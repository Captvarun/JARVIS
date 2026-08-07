import math
from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QRadialGradient, QConicalGradient
from PySide6.QtWidgets import QWidget

class ReactorOrbWidget(QWidget):
    """
    Animated Futuristic Arc Reactor Core Visualizer.
    Renders rotating sci-fi energy rings and pulsing core HUD visuals.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(220, 220)
        
        self.angle = 0
        self.pulse = 0.0
        self.pulse_direction = 1

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(30) # 33 FPS animation loop

    def _animate(self):
        self.angle = (self.angle + 2) % 360
        self.pulse += 0.03 * self.pulse_direction
        if self.pulse >= 1.0:
            self.pulse = 1.0
            self.pulse_direction = -1
        elif self.pulse <= 0.0:
            self.pulse = 0.0
            self.pulse_direction = 1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        side = min(width, height)
        center_x = width / 2
        center_y = height / 2
        radius = side * 0.45

        painter.translate(center_x, center_y)

        # 1. Outer Glowing Ambient Radial Gradient
        radial_grad = QRadialGradient(0, 0, radius)
        radial_grad.setColorAt(0.0, QColor(0, 240, 255, int(60 + 40 * self.pulse)))
        radial_grad.setColorAt(0.6, QColor(0, 136, 255, int(20 + 20 * self.pulse)))
        radial_grad.setColorAt(1.0, QColor(7, 11, 20, 0))
        painter.setBrush(radial_grad)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(-radius, -radius, radius * 2, radius * 2)

        # 2. Rotating Outer Segmented Arc Ring
        painter.save()
        painter.rotate(self.angle)
        outer_pen = QPen(QColor(0, 240, 255, 180), 2.5, Qt.DashLine)
        painter.setPen(outer_pen)
        painter.drawEllipse(QRectF(-radius * 0.8, -radius * 0.8, radius * 1.6, radius * 1.6))
        painter.restore()

        # 3. Rotating Counter Arc Ring
        painter.save()
        painter.rotate(-self.angle * 1.5)
        mid_pen = QPen(QColor(56, 189, 248, 220), 1.8, Qt.DotLine)
        painter.setPen(mid_pen)
        painter.drawEllipse(QRectF(-radius * 0.6, -radius * 0.6, radius * 1.2, radius * 1.2))
        painter.restore()

        # 4. Central Pulsing Core
        core_radius = radius * (0.3 + 0.05 * self.pulse)
        core_grad = QRadialGradient(0, 0, core_radius)
        core_grad.setColorAt(0.0, QColor(255, 255, 255, 240))
        core_grad.setColorAt(0.4, QColor(0, 240, 255, 200))
        core_grad.setColorAt(1.0, QColor(0, 136, 255, 0))
        painter.setBrush(core_grad)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(-core_radius, -core_radius, core_radius * 2, core_radius * 2)
