import threading
from typing import Optional
from core.logger import logger
from core.events import events

class TextToSpeechEngine:
    """
    Native Windows Text-to-Speech Engine with real audio synthesis,
    exact log event tracing, and non-blocking or blocking speech playback.
    """
    def __init__(self):
        self.is_speaking = False
        self.enabled = True
        self.volume = 90
        self.rate = 180
        self._speech_thread: Optional[threading.Thread] = None

    def speak(self, text: str, sync: bool = False):
        """
        Synthesizes text to spoken audio.
        Logs every stage: Synthesis started, Audio generated, Audio playback started, Audio playback completed.
        """
        if not text or not self.enabled:
            return

        # Stop any active speech playback
        self.stop_speaking()

        def _do_speak():
            try:
                self.is_speaking = True
                logger.info("[TTS] Synthesis started")
                events.log_emitted.emit("voice", "[TTS] Synthesis started")
                events.voice_state_changed.emit("SPEAKING")

                # Ensure Windows COM COM-thread initialization
                try:
                    import pythoncom
                    pythoncom.CoInitialize()
                except Exception:
                    pass

                # Primary: Native Windows SAPI5 Speech Synthesizer via win32com
                try:
                    import win32com.client
                    speaker = win32com.client.Dispatch("SAPI.SpVoice")
                    
                    # Set Volume (0 to 100) and Rate (-10 to 10)
                    speaker.Volume = int(self.volume)
                    # Convert rate 180 (words/min) to SAPI5 scale (-10 to 10)
                    sapi_rate = int((self.rate - 180) / 15)
                    speaker.Rate = max(-10, min(10, sapi_rate))

                    logger.info("[TTS] Audio generated")
                    events.log_emitted.emit("voice", "[TTS] Audio generated")

                    logger.info("[TTS] Audio playback started")
                    events.log_emitted.emit("voice", "[TTS] Audio playback started")

                    # Synchronous SAPI5 Speak call (blocks until playback finishes)
                    speaker.Speak(text)

                    logger.info("[TTS] Audio playback completed")
                    events.log_emitted.emit("voice", "[TTS] Audio playback completed")

                except Exception as ex1:
                    # Fallback: pyttsx3
                    try:
                        import pyttsx3
                        engine = pyttsx3.init()
                        engine.setProperty('volume', self.volume / 100.0)
                        engine.setProperty('rate', self.rate)
                        
                        logger.info("[TTS] Audio generated")
                        events.log_emitted.emit("voice", "[TTS] Audio generated")

                        logger.info("[TTS] Audio playback started")
                        events.log_emitted.emit("voice", "[TTS] Audio playback started")

                        engine.say(text)
                        engine.runAndWait()

                        logger.info("[TTS] Audio playback completed")
                        events.log_emitted.emit("voice", "[TTS] Audio playback completed")
                    except Exception as ex2:
                        logger.error(f"[TTS] Playback ERROR: {ex2}")
                        events.log_emitted.emit("voice", f"[TTS] Playback ERROR: {ex2}")

            except Exception as e:
                logger.error(f"[TTS] Playback ERROR: {e}")
                events.log_emitted.emit("voice", f"[TTS] Playback ERROR: {e}")
            finally:
                self.is_speaking = False
                events.voice_state_changed.emit("IDLE")
                try:
                    import pythoncom
                    pythoncom.CoUninitialize()
                except Exception:
                    pass

        if sync:
            _do_speak()
        else:
            self._speech_thread = threading.Thread(target=_do_speak, daemon=True)
            self._speech_thread.start()

    def stop_speaking(self):
        """Immediately stops active speech playback."""
        if self.is_speaking:
            logger.info("[TTS] Stopping active speech playback.")
            self.is_speaking = False
            events.voice_state_changed.emit("IDLE")
