from PySide6.QtWidgets import QLabel, QHBoxLayout
from ui.widgets.hud_panel import HUDPanel
from core.events import events

class SubsystemStatusWidget(HUDPanel):
    """
    Subsystem Status Panel for Voice, Vision, Plugins, and Network.
    Dynamically connects to central EventBus for live vision state updates.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        title = QLabel("SUBSYSTEM STATUS")
        title.setProperty("class", "hud-subtitle")
        self.content_layout.addWidget(title)

        self.vision_badge = None

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

            if name == "Vision Engine":
                self.vision_badge = badge

            box.addWidget(lbl)
            box.addStretch()
            box.addWidget(badge)

            self.content_layout.addLayout(box)

        self.content_layout.addStretch()

        # Connect to dynamic event signals
        events.vision_state_changed.connect(self._on_vision_state_changed)

    def _on_vision_state_changed(self, state: str):
        if not self.vision_badge:
            return

        state_upper = state.upper()
        if state_upper == "ANALYZING":
            color = "#f59e0b" # Amber
        elif state_upper == "READY":
            color = "#10b981" # Green
        else:
            color = "#38bdf8" # Blue STANDBY

        self.vision_badge.setText(f"[ {state_upper} ]")
        self.vision_badge.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-family: 'IBM Plex Mono', monospace;
                font-size: 10px;
                font-weight: bold;
            }}
        """)
