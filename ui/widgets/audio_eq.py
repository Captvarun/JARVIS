import random
from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QPainter, QColor, QBrush
from PySide6.QtWidgets import QWidget, QLabel
from ui.widgets.hud_panel import HUDPanel

class AudioEQWidget(HUDPanel):
    """
    Vertical EQ-Style Audio Meter Widget.
    Switches color palette to AMBER (#ffb455) during SPEAKING / Voice output state.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        title = QLabel("AUDIO LEVEL (EQ)")
        title.setProperty("class", "hud-subtitle")
        self.content_layout.addWidget(title)

        self.canvas = _EQCanvas()
        self.content_layout.addWidget(self.canvas, 1)

    def set_state(self, state_name: str):
        self.canvas.set_state(state_name)

class _EQCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(80)
        self.num_bars = 8
        self.bars = [0.2] * self.num_bars
        self.current_state = "IDLE"

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(50)

    def set_state(self, state_name: str):
        self.current_state = state_name

    def _animate(self):
        if self.current_state in ("LISTENING", "SPEAKING"):
            for i in range(self.num_bars):
                self.bars[i] = random.uniform(0.3, 0.95)
        else:
            for i in range(self.num_bars):
                self.bars[i] = random.uniform(0.08, 0.25)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        padding = 6
        step = (w - padding * 2) / self.num_bars
        bar_w = step * 0.55

        # Use Amber (#ffb455) during SPEAKING state, Cyan (#4fd0ff) otherwise
        if self.current_state == "SPEAKING":
            active_color = QColor(255, 180, 85) # AMBER
        else:
            active_color = QColor(79, 208, 255) # CYAN

        for i in range(self.num_bars):
            x = padding + i * step + (step - bar_w) / 2.0
            val = self.bars[i]
            bar_h = val * (h - 10)
            y = h - 5 - bar_h

            rect = QRectF(x, y, bar_w, bar_h)
            painter.setBrush(QBrush(active_color))
            painter.setPen(Qt.NoPen)
            painter.drawRect(rect)
