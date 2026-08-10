import threading
from typing import Optional
from core.logger import logger
from core.events import events

class TextToSpeechEngine:
    """
    Native Windows Text-to-Speech Engine with thread-safe session tracking,
    stale callback suppression, and serialized application state management.
    """
    def __init__(self):
        self.is_speaking = False
        self.enabled = True
        self.volume = 90
        self.rate = 180
        self._speech_thread: Optional[threading.Thread] = None

        self._lock = threading.Lock()
        self._session_counter: int = 0
        self._current_session_id: int = 0

    def speak(self, text: str, sync: bool = False):
        """
        Synthesizes text to spoken audio with unique session ID lifecycle management.
        """
        if not text or not self.enabled:
            return

        with self._lock:
            if self._current_session_id != 0:
                old_id = self._current_session_id
                logger.info(f"[TTS] Cancelling session={old_id}")
                logger.info(f"[TTS] Session invalidated: {old_id}")
                events.log_emitted.emit("voice", f"[TTS] Cancelling session={old_id}")
                events.log_emitted.emit("voice", f"[TTS] Session invalidated: {old_id}")

            self._session_counter += 1
            session_id = self._session_counter
            self._current_session_id = session_id

            logger.info(f"[TTS] Session created: {session_id}")
            events.log_emitted.emit("voice", f"[TTS] Session created: {session_id}")

        def _do_speak(s_id: int):
            with self._lock:
                if s_id != self._current_session_id:
                    logger.info(f"[TTS] Ignoring stale callback for session={s_id}")
                    logger.info(f"[TTS] Current session={self._current_session_id}")
                    events.log_emitted.emit("voice", f"[TTS] Ignoring stale callback for session={s_id}")
                    events.log_emitted.emit("voice", f"[TTS] Current session={self._current_session_id}")
                    return
                self.is_speaking = True
                logger.info("[State] SPEAKING")
                events.voice_state_changed.emit("SPEAKING")

            try:
                logger.info(f"[TTS] Playback started: session={s_id}")
                events.log_emitted.emit("voice", f"[TTS] Playback started: session={s_id}")

                logger.info("[TTS] Synthesis started")
                events.log_emitted.emit("voice", "[TTS] Synthesis started")

                # Ensure Windows COM-thread initialization
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
                    sapi_rate = int((self.rate - 180) / 15)
                    speaker.Rate = max(-10, min(10, sapi_rate))

                    logger.info("[TTS] Audio generated")
                    events.log_emitted.emit("voice", "[TTS] Audio generated")

                    # Synchronous SAPI5 Speak call
                    speaker.Speak(text)

                except Exception as ex1:
                    # Fallback: pyttsx3
                    try:
                        import pyttsx3
                        engine = pyttsx3.init()
                        engine.setProperty('volume', self.volume / 100.0)
                        engine.setProperty('rate', self.rate)
                        
                        logger.info("[TTS] Audio generated")
                        events.log_emitted.emit("voice", "[TTS] Audio generated")

                        engine.say(text)
                        engine.runAndWait()
                    except Exception as ex2:
                        logger.error(f"[TTS] Playback ERROR: {ex2}")
                        events.log_emitted.emit("voice", f"[TTS] Playback ERROR: {ex2}")

            except Exception as e:
                logger.error(f"[TTS] Playback ERROR: {e}")
                events.log_emitted.emit("voice", f"[TTS] Playback ERROR: {e}")
            finally:
                with self._lock:
                    if s_id != self._current_session_id:
                        logger.info(f"[TTS] Ignoring stale callback for session={s_id}")
                        logger.info(f"[TTS] Current session={self._current_session_id}")
                        events.log_emitted.emit("voice", f"[TTS] Ignoring stale callback for session={s_id}")
                        events.log_emitted.emit("voice", f"[TTS] Current session={self._current_session_id}")
                    else:
                        self.is_speaking = False
                        self._current_session_id = 0
                        logger.info(f"[TTS] Playback completed: session={s_id}")
                        logger.info("[State] IDLE")
                        events.log_emitted.emit("voice", f"[TTS] Playback completed: session={s_id}")
                        events.voice_state_changed.emit("IDLE")

                try:
                    import pythoncom
                    pythoncom.CoUninitialize()
                except Exception:
                    pass

        if sync:
            _do_speak(session_id)
        else:
            self._speech_thread = threading.Thread(target=_do_speak, args=(session_id,), daemon=True)
            self._speech_thread.start()

    def stop_speaking(self):
        """Immediately stops active speech playback and invalidates the session."""
        with self._lock:
            if self._current_session_id != 0:
                old_id = self._current_session_id
                logger.info("[TTS] Stopping active speech playback.")
                logger.info(f"[TTS] Cancelling session={old_id}")
                logger.info(f"[TTS] Session invalidated: {old_id}")
                events.log_emitted.emit("voice", f"[TTS] Cancelling session={old_id}")
                events.log_emitted.emit("voice", f"[TTS] Session invalidated: {old_id}")
                self._current_session_id = 0
                self.is_speaking = False
                logger.info("[State] IDLE")
                events.voice_state_changed.emit("IDLE")
