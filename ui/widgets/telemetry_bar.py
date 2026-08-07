from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QProgressBar
import psutil

class TelemetryBarWidget(QFrame):
    """
    HUD Telemetry Monitor Widget for CPU & RAM Metrics.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "hud-panel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(12)

        title = QLabel("SYSTEM TELEMETRY")
        title.setProperty("class", "hud-subtitle")
        layout.addWidget(title)

        # CPU Meter
        self.cpu_label = QLabel("CPU USAGE: 0%")
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(10, 15, 29, 0.8);
                border: 1px solid rgba(0, 240, 255, 0.3);
                border-radius: 4px;
                text-align: center;
                color: #00f0ff;
                font-weight: bold;
                height: 12px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0088ff, stop:1 #00f0ff);
                border-radius: 3px;
            }
        """)

        # RAM Meter
        self.ram_label = QLabel("RAM USAGE: 0%")
        self.ram_bar = QProgressBar()
        self.ram_bar.setStyleSheet(self.cpu_bar.styleSheet())

        layout.addWidget(self.cpu_label)
        layout.addWidget(self.cpu_bar)
        layout.addWidget(self.ram_label)
        layout.addWidget(self.ram_bar)

        layout.addStretch()

        # Telemetry update timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_metrics)
        self.timer.start(1500)
        self._update_metrics()

    def _update_metrics(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent

        self.cpu_label.setText(f"CPU LOAD: {cpu:.1f}%")
        self.cpu_bar.setValue(int(cpu))

        self.ram_label.setText(f"RAM LOAD: {ram:.1f}%")
        self.ram_bar.setValue(int(ram))
