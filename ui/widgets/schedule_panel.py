from PySide6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QFrame
from ui.widgets.hud_panel import HUDPanel

class SchedulePanelWidget(HUDPanel):
    """
    Today's Schedule & Task List Panel for Right Column.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        title = QLabel("TODAY'S SCHEDULE")
        title.setProperty("class", "hud-subtitle")
        self.content_layout.addWidget(title)

        tasks = [
            ("09:30 AM", "Deep Code Session"),
            ("02:00 PM", "System Review"),
            ("05:30 PM", "AI Model Fine-tuning"),
            ("08:00 PM", "Architecture Check")
        ]

        for time_str, event_name in tasks:
            item_box = QHBoxLayout()
            item_box.setSpacing(8)

            badge = QLabel(time_str)
            badge.setStyleSheet("""
                QLabel {
                    background-color: rgba(79, 208, 255, 0.15);
                    color: #4fd0ff;
                    border: 1px solid rgba(79, 208, 255, 0.3);
                    border-radius: 3px;
                    padding: 2px 6px;
                    font-family: 'IBM Plex Mono', monospace;
                    font-size: 10px;
                    font-weight: 600;
                }
            """)

            label = QLabel(event_name)
            label.setStyleSheet("color: #cbd5e1; font-size: 12px; font-weight: 600;")

            item_box.addWidget(badge)
            item_box.addWidget(label, 1)

            self.content_layout.addLayout(item_box)

        self.content_layout.addStretch()
