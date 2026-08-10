import time
import unittest
from engine.voice.text_to_speech import TextToSpeechEngine
from core.events import events

class TestTTSLifecycle(unittest.TestCase):
    def setUp(self):
        self.tts = TextToSpeechEngine()
        self.recorded_states = []
        events.voice_state_changed.connect(lambda s: self.recorded_states.append(s))

    def test_session_creation_and_cancellation(self):
        self.tts.speak("Session A text")
        s_id_1 = self.tts._current_session_id
        self.assertGreater(s_id_1, 0)

        self.tts.speak("Session B text")
        s_id_2 = self.tts._current_session_id
        self.assertGreater(s_id_2, s_id_1)

    def test_interruption_chain_state_serialization(self):
        # A -> interrupt B -> interrupt C
        self.tts.speak("Session A")
        self.tts.speak("Session B")
        self.tts.speak("Session C", sync=True)

        # Final state MUST end in IDLE, without stale callback state drops
        self.assertFalse(self.tts.is_speaking)
        self.assertEqual(self.tts._current_session_id, 0)
        self.assertEqual(self.recorded_states[-1], "IDLE")

if __name__ == "__main__":
    unittest.main()
