from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLabel, QProgressBar
import psutil
from ui.widgets.hud_panel import HUDPanel

class DeviceSnapshotWidget(HUDPanel):
    """
    Device System Snapshot Panel displaying CPU, RAM, and Disk load meters.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        title = QLabel("DEVICE SNAPSHOT")
        title.setProperty("class", "hud-subtitle")
        self.content_layout.addWidget(title)

        # CPU
        self.cpu_lbl = QLabel("CPU LOAD: 0.0%")
        self.cpu_lbl.setProperty("class", "hud-data")
        self.cpu_bar = self._make_bar()
        self.content_layout.addWidget(self.cpu_lbl)
        self.content_layout.addWidget(self.cpu_bar)

        # RAM
        self.ram_lbl = QLabel("RAM LOAD: 0.0%")
        self.ram_lbl.setProperty("class", "hud-data")
        self.ram_bar = self._make_bar()
        self.content_layout.addWidget(self.ram_lbl)
        self.content_layout.addWidget(self.ram_bar)

        # DISK
        self.disk_lbl = QLabel("DISK LOAD: 0.0%")
        self.disk_lbl.setProperty("class", "hud-data")
        self.disk_bar = self._make_bar()
        self.content_layout.addWidget(self.disk_lbl)
        self.content_layout.addWidget(self.disk_bar)

        # Telemetry Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_telemetry)
        self.timer.start(1500)
        self._update_telemetry()

    def _make_bar(self) -> QProgressBar:
        bar = QProgressBar()
        bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(3, 5, 9, 0.8);
                border: 1px solid rgba(79, 208, 255, 0.3);
                border-radius: 3px;
                text-align: center;
                color: #4fd0ff;
                font-family: 'IBM Plex Mono', monospace;
                font-size: 10px;
                font-weight: bold;
                height: 10px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0088ff, stop:1 #4fd0ff);
                border-radius: 2px;
            }
        """)
        return bar

    def _update_telemetry(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent

        self.cpu_lbl.setText(f"CPU LOAD: {cpu:.1f}%")
        self.cpu_bar.setValue(int(cpu))

        self.ram_lbl.setText(f"RAM LOAD: {ram:.1f}%")
        self.ram_bar.setValue(int(ram))

        self.disk_lbl.setText(f"DISK LOAD: {disk:.1f}%")
        self.disk_bar.setValue(int(disk))
