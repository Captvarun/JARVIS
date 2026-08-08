import unittest
from engine.voice.voice_engine import VoiceEngine, voice_engine
from engine.voice.text_to_speech import TextToSpeechEngine

class TestVoiceEngine(unittest.TestCase):
    def setUp(self):
        self.voice = VoiceEngine()
        self.voice.on_initialize()

    def test_voice_engine_initialization(self):
        self.assertIsNotNone(self.voice.tts)
        self.assertIsNotNone(self.voice.stt)
        self.assertTrue(self.voice.tts.enabled)

    def test_tts_stop_speaking(self):
        self.voice.stop_speaking()
        self.assertFalse(self.voice.tts.is_speaking)

    def test_push_to_talk_handling(self):
        # Graceful handling without throwing exceptions
        transcript = self.voice.trigger_push_to_talk()
        # Should return text or None without crashing
        self.assertTrue(transcript is None or isinstance(transcript, str))

if __name__ == "__main__":
    unittest.main()
