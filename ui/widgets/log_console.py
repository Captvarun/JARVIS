from datetime import datetime
from PySide6.QtCore import Slot, Signal
from PySide6.QtWidgets import QLabel, QTextEdit, QLineEdit, QPushButton, QHBoxLayout
from ui.widgets.hud_panel import HUDPanel

class IntegratedConsolePanel(HUDPanel):
    """
    Unified Console Panel embedding log stream and command prompt line in a single chamfered panel.
    Supports tagged message formats: [core], [user], [voice], [vision], [plugin], [personality], [error].
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
        
        # Initial logs
        t = datetime.now().strftime("%H:%M:%S")
        self.log_edit.append(f"<font color='#64748b'>[{t}]</font> <font color='#8fe3ff'><b>[core]</b> System initialized</font>")
        self.log_edit.append(f"<font color='#64748b'>[{t}]</font> <font color='#10b981'><b>[voice]</b> Speech synthesis engine online</font>")
        self.log_edit.append(f"<font color='#64748b'>[{t}]</font> <font color='#f59e0b'><b>[personality]</b> Adaptive Profile: COMPANION</font>")
        self.log_edit.append(f"<font color='#64748b'>[{t}]</font> <font color='#4fd0ff'><b>[user]</b> hello JARVIS</font>")
        self.log_edit.append(f"<font color='#64748b'>[{t}]</font> <font color='#8fe3ff'><b>[jarvis]</b> Hello, Varun. Systems are online.</font>\n")

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
            self.append_tagged_msg("user", text)
            self.command_submitted.emit(text)

    def append_tagged_msg(self, tag: str, text: str):
        t = datetime.now().strftime("%H:%M:%S")
        tag_colors = {
            "core": "#8fe3ff",
            "jarvis": "#8fe3ff",
            "user": "#4fd0ff",
            "voice": "#10b981",
            "vision": "#38bdf8",
            "plugin": "#f59e0b",
            "personality": "#f59e0b",
            "error": "#ef4444"
        }
        color = tag_colors.get(tag.lower(), "#38bdf8")
        
        # Replace newlines with break tags for multiline personality profiles
        formatted_text = text.replace("\n", "<br/>")
        self.log_edit.append(f"<font color='#64748b'>[{t}]</font> <font color='{color}'><b>[{tag}]</b> {formatted_text}</font>")

    @Slot(str)
    def append_user_msg(self, text: str):
        self.append_tagged_msg("user", text)

    @Slot(str)
    def append_system_msg(self, text: str):
        self.append_tagged_msg("jarvis", text)
