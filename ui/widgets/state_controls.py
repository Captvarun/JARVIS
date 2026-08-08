from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton

class StateControlsWidget(QWidget):
    """
    Developer State Control Bar for testing reactor transitions.
    Buttons: [IDLE] [LISTENING] [THINKING] [SPEAKING] [ERROR]
    """
    state_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.states = ["IDLE", "LISTENING", "THINKING", "SPEAKING", "ERROR"]
        self.buttons = {}

        for s in self.states:
            btn = QPushButton(f"[ {s} ]")
            btn.setProperty("class", "state-btn")
            if s == "IDLE":
                btn.setProperty("class", "state-btn active-idle")
            btn.clicked.connect(lambda _, name=s: self._select_state(name))
            layout.addWidget(btn)
            self.buttons[s] = btn

    def _select_state(self, name: str):
        for s, btn in self.buttons.items():
            if s == name:
                class_map = {
                    "IDLE": "state-btn active-idle",
                    "LISTENING": "state-btn active-listening",
                    "THINKING": "state-btn active-thinking",
                    "SPEAKING": "state-btn active-speaking",
                    "ERROR": "state-btn active-error"
                }
                btn.setProperty("class", class_map.get(s, "state-btn"))
            else:
                btn.setProperty("class", "state-btn")
            btn.setStyle(btn.style())
            
        self.state_requested.emit(name)
