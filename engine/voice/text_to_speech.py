import threading
from typing import Optional
from core.logger import logger
from core.events import events

class TextToSpeechEngine:
    """
    Non-blocking Text-to-Speech Engine utilizing native Windows SAPI5 / pyttsx3.
    """
    def __init__(self):
        self.is_speaking = False
        self.enabled = True
        self.volume = 90
        self.rate = 180
        self._speech_thread: Optional[threading.Thread] = None

    def speak(self, text: str, on_complete_cb=None):
        """Synthesizes text to spoken audio off the main GUI thread."""
        if not text or not self.enabled:
            if on_complete_cb:
                on_complete_cb()
            return

        # Stop any existing speech thread
        self.stop_speaking()

        def _worker():
            try:
                self.is_speaking = True
                logger.info(f"[TTS] Synthesizing speech: '{text}'")
                events.voice_state_changed.emit("SPEAKING")

                # Try native Windows SAPI5 via pyttsx3 or win32com
                try:
                    import pyttsx3
                    engine = pyttsx3.init()
                    engine.setProperty('rate', self.rate)
                    engine.setProperty('volume', self.volume / 100.0)
                    engine.say(text)
                    engine.runAndWait()
                    engine.stop()
                except Exception:
                    # Windows PowerShell SAPI fallback if pyttsx3 is unavailable
                    import subprocess
                    ps_cmd = f"Add-Type -AssemblyName System.Speech; \$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; \$synth.Rate = 1; \$synth.Speak('{text}')"
                    subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)

            except Exception as e:
                logger.error(f"[TTS] Speech synthesis error: {e}")
            finally:
                self.is_speaking = False
                events.voice_state_changed.emit("IDLE")
                if on_complete_cb:
                    on_complete_cb()

        self._speech_thread = threading.Thread(target=_worker, daemon=True)
        self._speech_thread.start()

    def stop_speaking(self):
        """Immediately stops/cancels active speech playback."""
        if self.is_speaking:
            logger.info("[TTS] Stopping active speech playback.")
            self.is_speaking = False
            events.voice_state_changed.emit("IDLE")
