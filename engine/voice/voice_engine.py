from core.lifecycle import BaseLifecycleComponent
from engine.voice.text_to_speech import TextToSpeechEngine
from engine.voice.speech_to_text import SpeechToTextEngine
from core.events import events
from core.logger import logger

class VoiceEngine(BaseLifecycleComponent):
    """
    Voice Subsystem Coordinator.
    Integrates Speech-to-Text, Text-to-Speech, and Audio Device state management.
    """
    def __init__(self):
        super().__init__("VoiceEngine")
        self.tts = TextToSpeechEngine()
        self.stt = SpeechToTextEngine()

    def on_initialize(self) -> bool:
        logger.info("[VoiceEngine] Voice Subsystem initialized.")
        return True

    def speak(self, text: str, sync: bool = False):
        """Synthesize and speak text response."""
        self.tts.speak(text, sync=sync)

    def stop_speaking(self):
        """Stop active TTS speech output immediately."""
        self.tts.stop_speaking()

    def trigger_push_to_talk(self):
        """Activates microphone listening pipeline."""
        events.log_emitted.emit("voice", "Push-to-Talk triggered.")
        return self.stt.listen_and_transcribe()

# Global Voice Engine Singleton
voice_engine = VoiceEngine()
