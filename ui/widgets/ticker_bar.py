import time
from datetime import datetime
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel
from core.events import events
from core.state import state
from core.config import config

class TickerBarWidget(QFrame):
    """
    Top Ticker Bar for system mode, operator identity, uptime, location, dynamic model, and clock.
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
        location_str = config.get("system.location", "LOC INDIA")
        model_str = state.get("active_model", config.get("app.model", "GPT-4o ●●●"))

        self.uptime_chip = self._make_chip("UP 00:00:00")
        self.mode_chip = self._make_chip("MODE ONLINE")
        self.op_chip = self._make_chip("OP VARUN")
        self.loc_chip = self._make_chip(location_str)
        self.model_chip = self._make_chip(f"MODEL {model_str}")

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

        # Connect EventBus state signal
        events.state_updated.connect(self._on_state_updated)

        # Clock Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_ticker)
        self.timer.start(1000)
        self._update_ticker()

    def _make_chip(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setProperty("class", "ticker-chip")
        return lbl

    def _on_state_updated(self, key: str, value: object):
        if key == "active_model":
            self.model_chip.setText(f"MODEL {value}")
        elif key == "status":
            self.mode_chip.setText(f"MODE {str(value).upper()}")

    def _update_ticker(self):
        # Update Clock
        now = datetime.now().strftime("%H:%M:%S")
        self.clock_label.setText(now)

        # Update Uptime
        elapsed = int(time.time() - self.start_time)
        hrs, rem = divmod(elapsed, 3600)
        mins, secs = divmod(rem, 60)
        self.uptime_chip.setText(f"UP {hrs:02d}:{mins:02d}:{secs:02d}")
