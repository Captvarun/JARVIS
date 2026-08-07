from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton
from PySide6.QtCore import Signal

class PromptBarWidget(QWidget):
    """
    Cyber Command Prompt Bar with Execute Button.
    """
    command_submitted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.input_field = QLineEdit()
        self.input_field.setProperty("class", "hud-input")
        self.input_field.setPlaceholderText("Enter command or query JARVIS...")
        self.input_field.returnPressed.connect(self._emit_submit)

        self.send_btn = QPushButton("EXECUTE")
        self.send_btn.setProperty("class", "hud-btn-primary")
        self.send_btn.clicked.connect(self._emit_submit)

        layout.addWidget(self.input_field, 1)
        layout.addWidget(self.send_btn)

    def _emit_submit(self):
        text = self.input_field.text().strip()
        if text:
            self.input_field.clear()
            self.command_submitted.emit(text)
