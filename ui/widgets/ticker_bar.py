import time
from datetime import datetime
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel

class TickerBarWidget(QFrame):
    """
    Top Ticker Bar for system mode, operator identity, uptime, and precision digital clock.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(7, 12, 22, 0.9);
                border-bottom: 1px solid rgba(79, 208, 255, 0.25);
            }
        """)

        self.start_time = time.time()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(8)

        # Micro Telemetry Chips
        self.uptime_chip = self._make_chip("UP 00:00:00")
        self.mode_chip = self._make_chip("MODE ONLINE")
        self.op_chip = self._make_chip("OP VARUN")
        self.loc_chip = self._make_chip("LOC IN")
        self.model_chip = self._make_chip("MODEL GPT-4o ●●●")

        layout.addWidget(self.uptime_chip)
        layout.addWidget(self.mode_chip)
        layout.addWidget(self.op_chip)
        layout.addWidget(self.loc_chip)
        layout.addWidget(self.model_chip)

        layout.addStretch()

        # Real-time Precision Clock
        self.clock_label = QLabel("--:--:--")
        self.clock_label.setStyleSheet("""
            QLabel {
                color: #4fd0ff;
                font-family: 'IBM Plex Mono', 'Consolas', monospace;
                font-size: 14px;
                font-weight: 700;
                letter-spacing: 1px;
            }
        """)
        layout.addWidget(self.clock_label)

        # Clock Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_ticker)
        self.timer.start(1000)
        self._update_ticker()

    def _make_chip(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setProperty("class", "ticker-chip")
        return lbl

    def _update_ticker(self):
        # Update Clock
        now = datetime.now().strftime("%H:%M:%S")
        self.clock_label.setText(now)

        # Update Uptime
        elapsed = int(time.time() - self.start_time)
        hrs, rem = divmod(elapsed, 3600)
        mins, secs = divmod(rem, 60)
        self.uptime_chip.setText(f"UP {hrs:02d}:{mins:02d}:{secs:02d}")
