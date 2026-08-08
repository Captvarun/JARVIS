from PySide6.QtCore import Slot, Signal
from PySide6.QtWidgets import QLabel, QTextEdit, QLineEdit, QPushButton, QHBoxLayout
from ui.widgets.hud_panel import HUDPanel

class IntegratedConsolePanel(HUDPanel):
    """
    Unified Console Panel embedding both log stream and command prompt in the same HUD panel.
    """
    command_submitted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        header = QLabel("CONSOLE & SYSTEM STREAM")
        header.setProperty("class", "hud-subtitle")
        self.content_layout.addWidget(header)

        # Log Text Box
        self.log_edit = QTextEdit()
        self.log_edit.setProperty("class", "hud-log")
        self.log_edit.setReadOnly(True)
        self.log_edit.setPlaceholderText(">>> JARVIS Command Log & Response Stream...")
        self.log_edit.append("<font color='#475569'>[00:44:12] [core] System initialized</font>")
        self.log_edit.append("<font color='#475569'>[00:44:13] [core] Neural interface ready</font>")
        self.log_edit.append("<font color='#4fd0ff'>[00:44:15] [user] Open my workspace</font>")
        self.log_edit.append("<font color='#8fe3ff'>[00:44:16] [core] Launching IDE...</font>\n")

        self.content_layout.addWidget(self.log_edit, 1)

        # Embedded Input Bar
        input_box = QHBoxLayout()
        input_box.setSpacing(8)

        self.prompt_input = QLineEdit()
        self.prompt_input.setProperty("class", "hud-input")
        self.prompt_input.setPlaceholderText("> Ask JARVIS or type a command...")
        self.prompt_input.returnPressed.connect(self._emit_command)

        send_btn = QPushButton("↵")
        send_btn.setProperty("class", "hud-btn-primary")
        send_btn.setFixedWidth(40)
        send_btn.clicked.connect(self._emit_command)

        input_box.addWidget(self.prompt_input, 1)
        input_box.addWidget(send_btn)

        self.content_layout.addLayout(input_box)

    def _emit_command(self):
        text = self.prompt_input.text().strip()
        if text:
            self.prompt_input.clear()
            self.append_user_msg(text)
            self.command_submitted.emit(text)

    @Slot(str)
    def append_user_msg(self, text: str):
        self.log_edit.append(f"<font color='#4fd0ff'><b>[user]</b> {text}</font>")

    @Slot(str)
    def append_system_msg(self, text: str):
        self.log_edit.append(f"<font color='#8fe3ff'><b>[core]</b> {text}</font>\n")
