import time
from PySide6.QtCore import QThread, Signal, Slot
from core.brain.brain import brain
from core.events import events
from core.logger import logger

class BrainWorkerThread(QThread):
    """
    Asynchronous Worker Thread for processing JARVIS Brain queries.
    Prevents the PySide6 UI thread from locking during processing.
    """
    response_ready = Signal(str, str) # intent, response_text
    state_changed = Signal(str)       # IDLE, LISTENING, THINKING, SPEAKING, ERROR

    def __init__(self, prompt: str):
        super().__init__()
        self.prompt = prompt

    def run(self):
        try:
            # 1. Listening State
            self.state_changed.emit("LISTENING")
            time.sleep(0.2)

            # 2. Thinking State
            self.state_changed.emit("THINKING")
            time.sleep(0.3)

            # 3. Brain Processing
            response = brain.process_command(self.prompt)

            # 4. Speaking State (Response Generation)
            self.state_changed.emit("SPEAKING")
            time.sleep(0.5)

            # Emit Result
            self.response_ready.emit(response.intent, response.text)

            # Return to IDLE
            self.state_changed.emit("IDLE")

        except Exception as e:
            logger.error(f"[BrainWorkerThread] Worker Error: {e}")
            self.state_changed.emit("ERROR")
            self.response_ready.emit("error", "An internal error occurred.")
            time.sleep(1.0)
            self.state_changed.emit("IDLE")
