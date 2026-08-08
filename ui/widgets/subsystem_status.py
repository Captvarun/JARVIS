from PySide6.QtWidgets import QLabel, QHBoxLayout
from ui.widgets.hud_panel import HUDPanel

class SubsystemStatusWidget(HUDPanel):
    """
    Subsystem Status Panel for Voice, Vision, Plugins, and Network.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        title = QLabel("SUBSYSTEM STATUS")
        title.setProperty("class", "hud-subtitle")
        self.content_layout.addWidget(title)

        subsystems = [
            ("Voice Engine", "ONLINE", "#10b981"),
            ("Vision Engine", "STANDBY", "#38bdf8"),
            ("Plugins Engine", "ACTIVE", "#10b981"),
            ("Network Subsystem", "CONNECTED", "#10b981")
        ]

        for name, status, color_hex in subsystems:
            box = QHBoxLayout()
            box.setSpacing(6)

            lbl = QLabel(name)
            lbl.setStyleSheet("color: #cbd5e1; font-size: 12px; font-weight: 600;")

            badge = QLabel(f"[ {status} ]")
            badge.setStyleSheet(f"""
                QLabel {{
                    color: {color_hex};
                    font-family: 'IBM Plex Mono', monospace;
                    font-size: 10px;
                    font-weight: bold;
                }}
            """)

            box.addWidget(lbl)
            box.addStretch()
            box.addWidget(badge)

            self.content_layout.addLayout(box)

        self.content_layout.addStretch()
