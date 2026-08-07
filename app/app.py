import sys
from PySide6.QtWidgets import QApplication
from ui.windows.main_window import JARVISMainWindow
from core.logger import logger

def run_app():
    """
    Launch the PySide6 JARVIS UI Application.
    """
    app = QApplication(sys.argv)
    app.setApplicationName("JARVIS AI")

    main_window = JARVISMainWindow()
    main_window.show()

    logger.info("JARVIS GUI application running.")
    sys.exit(app.exec())
