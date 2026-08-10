import unittest
from core.brain.brain import JarvisBrain
from core.brain.intent import IntentDetector, IntentCategory
from core.brain.context import ContextManager
from core.personality.personality_engine import personality_engine

class TestJarvisBrain(unittest.TestCase):
    def setUp(self):
        personality_engine.state.reset()
        self.brain = JarvisBrain()
        self.brain.initialize()
        self.brain.context.reset_memory()

    def test_intent_detection(self):
        detector = IntentDetector()
        self.assertEqual(detector.detect("hello JARVIS"), IntentCategory.CONVERSATION)
        self.assertEqual(detector.detect("what time is it"), IntentCategory.INFORMATION_REQUEST)
        self.assertEqual(detector.detect("show system status"), IntentCategory.SYSTEM_COMMAND)
        self.assertEqual(detector.detect("what is my project called"), IntentCategory.MEMORY)
        self.assertEqual(detector.detect("open google search"), IntentCategory.PLUGIN)
        self.assertEqual(detector.detect("what's the sarcasm level"), IntentCategory.GET_PERSONALITY)

    def test_brain_hello_command(self):
        res = self.brain.process_command("hello JARVIS")
        self.assertTrue(res.success)

    def test_conversational_queries(self):
        res_how = self.brain.process_command("how are you doing today")
        self.assertNotIn("Processed query:", res_how.text)
        self.assertNotIn("Systems are operational.", res_how.text)

        res_tired = self.brain.process_command("i'm tired")
        self.assertIn("rest", res_tired.text.lower())

        res_followup = self.brain.process_command("what should I do?")
        self.assertIn("rest", res_followup.text.lower())

    def test_roast_command(self):
        res_roast = self.brain.process_command("jarvis roast me")
        self.assertNotIn("Processed query:", res_roast.text)
        self.assertNotIn("Systems are operational.", res_roast.text)

    def test_system_command_telemetry(self):
        res_sys = self.brain.process_command("show system status")
        self.assertTrue(res_sys.success)
        self.assertIn("CPU Load", res_sys.text)

    def test_context_bounding(self):
        ctx = ContextManager(max_turns=4)
        for i in range(10):
            ctx.add_turn(f"user msg {i}", f"jarvis resp {i}")
        self.assertLessEqual(len(ctx.history), 4)

if __name__ == "__main__":
    unittest.main()
