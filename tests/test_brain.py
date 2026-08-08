import unittest
from core.brain.brain import JarvisBrain
from core.brain.intent import IntentDetector, IntentCategory
from core.brain.context import ContextManager
from core.brain.router import CommandRouter
from core.brain.provider import LocalMockProvider

class TestJarvisBrain(unittest.TestCase):
    def setUp(self):
        self.brain = JarvisBrain()
        self.brain.initialize()

    def test_intent_detection(self):
        detector = IntentDetector()
        self.assertEqual(detector.detect("hello JARVIS"), IntentCategory.CONVERSATION)
        self.assertEqual(detector.detect("what time is it"), IntentCategory.INFORMATION_REQUEST)
        self.assertEqual(detector.detect("show system status"), IntentCategory.SYSTEM_COMMAND)
        self.assertEqual(detector.detect("what is my project called"), IntentCategory.MEMORY)
        self.assertEqual(detector.detect("open google search"), IntentCategory.PLUGIN)

    def test_brain_hello_command(self):
        res = self.brain.process_command("hello JARVIS")
        self.assertTrue(res.success)
        self.assertIn("Varun", res.text)
        self.assertIn("systems are online", res.text.lower())

    def test_brain_time_command(self):
        res = self.brain.process_command("what time is it")
        self.assertTrue(res.success)
        self.assertIn("local time is", res.text.lower())

    def test_brain_system_status_command(self):
        res = self.brain.process_command("show system status")
        self.assertTrue(res.success)
        self.assertIn("CPU Load", res.text)
        self.assertIn("RAM Load", res.text)

    def test_brain_memory_command(self):
        res = self.brain.process_command("what is my project called?")
        self.assertTrue(res.success)
        self.assertIn("JARVIS", res.text)

    def test_context_bounding(self):
        ctx = ContextManager(max_turns=4)
        for i in range(10):
            ctx.add_turn("user", f"msg {i}")
        history = ctx.get_history()
        self.assertLessEqual(len(history), 4)

if __name__ == "__main__":
    unittest.main()
