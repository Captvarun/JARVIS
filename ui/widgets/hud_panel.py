from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath
from PySide6.QtWidgets import QWidget, QVBoxLayout

class HUDPanel(QWidget):
    """
    Chamfered HUD Panel with 45-degree diagonal cut corners
    and translucent glassmorphism background + glowing cyan border.
    """
    def __init__(self, parent=None, corner_cut: float = 10.0):
        super().__init__(parent)
        self.corner_cut = corner_cut
        self.active_border = False
        
        # Transparent background so QPainter handles panel shape
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # Main internal layout
        self.content_layout = QVBoxLayout(self)
        self.content_layout.setContentsMargins(14, 14, 14, 14)
        self.content_layout.setSpacing(10)

    def set_active(self, active: bool):
        self.active_border = active
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = float(self.width() - 1)
        h = float(self.height() - 1)
        c = self.corner_cut

        # Create polygon path with 45-degree diagonal cut corners (Top-Left & Bottom-Right)
        path = QPainterPath()
        path.moveTo(c, 0)
        path.lineTo(w, 0)
        path.lineTo(w, h - c)
        path.lineTo(w - c, h)
        path.lineTo(0, h)
        path.lineTo(0, c)
        path.closeSubpath()

        # Background Fill
        bg_color = QColor(10, 18, 32, 200) # Translucent dark background
        painter.setBrush(QBrush(bg_color))

        # Border Pen
        if self.active_border:
            border_pen = QPen(QColor(79, 208, 255, 230), 1.5)
        else:
            border_pen = QPen(QColor(79, 208, 255, 60), 1.0)

        painter.setPen(border_pen)
        painter.drawPath(path)
