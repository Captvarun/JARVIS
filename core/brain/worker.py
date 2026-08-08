import time
from PySide6.QtCore import QThread, Signal
from core.brain.brain import brain
from engine.voice.voice_engine import voice_engine
from core.events import events
from core.logger import logger

class BrainWorkerThread(QThread):
    """
    Asynchronous Worker Thread for processing JARVIS Brain & Voice queries.
    Prevents the PySide6 UI thread from locking during processing or TTS synthesis.
    """
    response_ready = Signal(str, str) # intent, response_text
    state_changed = Signal(str)       # IDLE, LISTENING, THINKING, SPEAKING, ERROR

    def __init__(self, prompt: str, is_spoken: bool = False):
        super().__init__()
        self.prompt = prompt
        self.is_spoken = is_spoken

    def run(self):
        try:
            # 1. Listening State (if spoken input)
            if self.is_spoken:
                self.state_changed.emit("LISTENING")
                time.sleep(0.3)

            # 2. Thinking State
            self.state_changed.emit("THINKING")
            time.sleep(0.2)

            # 3. Brain Processing
            response = brain.process_command(self.prompt)

            # 4. Speaking State & TTS Synthesis
            if response.text and response.intent != "voice_control":
                self.state_changed.emit("SPEAKING")
                # Trigger TTS synthesis
                voice_engine.speak(response.text)
                time.sleep(0.5)

            # Emit Result to Console Stream
            self.response_ready.emit(response.intent, response.text)

            # Return to IDLE
            self.state_changed.emit("IDLE")

        except Exception as e:
            logger.error(f"[BrainWorkerThread] Worker Error: {e}")
            self.state_changed.emit("ERROR")
            self.response_ready.emit("error", "An internal error occurred.")
            time.sleep(1.0)
            self.state_changed.emit("IDLE")
