from PySide6.QtWidgets import QTextEdit
from PySide6.QtCore import Slot

class LogConsoleWidget(QTextEdit):
    """
    Futuristic HUD Log Console Widget.
    Displays formatted prompt histories, system responses, and log streams.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "hud-log")
        self.setReadOnly(True)
        self.setPlaceholderText(">>> JARVIS Command Log & Response Stream...")
        self.append(">>> Initializing JARVIS Production Skeleton [Milestone 1]...")
        self.append(">>> All Engine Subsystems & Plugins Loaded.")
        self.append(">>> System ready for user input.\n")

    @Slot(str)
    def append_user_msg(self, text: str):
        self.append(f"<font color='#00f0ff'><b>USER:</b> {text}</font>")

    @Slot(str)
    def append_system_msg(self, text: str):
        self.append(f"<font color='#38bdf8'><b>JARVIS:</b> {text}</font>\n")

    @Slot(str, str)
    def append_log(self, level: str, msg: str):
        self.append(f"<font color='#64748b'>[{level}] {msg}</font>")
