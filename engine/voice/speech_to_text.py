import time
from typing import Optional
from core.logger import logger
from core.events import events

class SpeechToTextEngine:
    """
    Microphone Capture & Speech-to-Text Transcriber.
    Supports push-to-talk microphone audio capture.
    """
    def __init__(self):
        self.is_listening = False
        self.enabled = True

    def listen_and_transcribe(self, duration: int = 5) -> Optional[str]:
        """
        Captures audio from microphone and returns transcribed text.
        Handles missing microphone or recognition failures gracefully.
        """
        if not self.enabled:
            return None

        self.is_listening = True
        events.voice_state_changed.emit("LISTENING")
        events.log_emitted.emit("voice", "Microphone activated. Listening...")

        try:
            # Try speech_recognition package if installed
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio = r.listen(source, timeout=duration, phrase_time_limit=duration)
                events.voice_state_changed.emit("THINKING")
                transcript = r.recognize_google(audio)
                events.log_emitted.emit("voice", f"Transcript: '{transcript}'")
                return transcript
        except Exception as e:
            logger.warning(f"[STT] Speech recognition capture info/fallback: {e}")
            events.log_emitted.emit("voice", "Microphone listening complete (Push-to-Talk).")
            return None
        finally:
            self.is_listening = False
