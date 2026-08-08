from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QBrush, QPen
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from ui.widgets.hud_panel import HUDPanel

class ActivityGraphWidget(HUDPanel):
    """
    Weekly Development / Commit Activity Telemetry Chart Widget.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        title = QLabel("WEEKLY DEVELOPMENT ACTIVITY")
        title.setProperty("class", "hud-subtitle")
        self.content_layout.addWidget(title)

        self.chart_canvas = _ActivityCanvas()
        self.content_layout.addWidget(self.chart_canvas, 1)

class _ActivityCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(90)
        # Mock activity values (commits/hours per day)
        self.days = ["M", "T", "W", "T", "F", "S", "S"]
        self.values = [45, 80, 60, 95, 30, 75, 50]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        n = len(self.values)
        padding = 10
        bar_area_w = w - (padding * 2)
        step = bar_area_w / n
        bar_w = step * 0.45
        max_val = max(self.values)

        for i, val in enumerate(self.values):
            x = padding + i * step + (step - bar_w) / 2.0
            bar_h = (val / max_val) * (h - 28)
            y = h - 18 - bar_h

            # Draw glowing bar
            rect = QRectF(x, y, bar_w, bar_h)
            bar_color = QColor(79, 208, 255, 180 if val < 90 else 240)
            painter.setBrush(QBrush(bar_color))
            painter.setPen(Qt.NoPen)
            painter.drawRect(rect)

            # Draw Day Label
            painter.setPen(QPen(QColor(100, 116, 139), 1))
            painter.setFont(self.font())
            painter.drawText(QRectF(x - 5, h - 16, bar_w + 10, 14), Qt.AlignCenter, self.days[i])
