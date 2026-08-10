import unittest
from core.brain.intent import IntentDetector, IntentCategory
from core.brain.brain import JarvisBrain
from engine.vision.vision_engine import vision_engine

class TestMilestone6VisionEngine(unittest.TestCase):
    def setUp(self):
        self.brain = JarvisBrain()
        self.brain.initialize()
        self.brain.context.reset_memory()

    def test_vision_intent_detection(self):
        detector = IntentDetector()
        phrases = [
            "JARVIS, analyze my screen.",
            "what am I looking at?",
            "look at my screen",
            "what's on my screen?",
            "read my screen",
            "inspect my screen",
            "what error am I getting?",
            "what's wrong with this?",
            "read that error"
        ]
        for p in phrases:
            self.assertEqual(detector.detect(p), IntentCategory.VISION_SCREEN_ANALYSIS, f"Failed for prompt: {p}")

    def test_non_vision_commands_do_not_trigger_vision(self):
        detector = IntentDetector()
        self.assertNotEqual(detector.detect("What's my RAM usage?"), IntentCategory.VISION_SCREEN_ANALYSIS)
        self.assertNotEqual(detector.detect("Tell me a joke"), IntentCategory.VISION_SCREEN_ANALYSIS)
        self.assertNotEqual(detector.detect("Open Google"), IntentCategory.VISION_SCREEN_ANALYSIS)

    def test_privacy_check_enforcement(self):
        # Background/automatic attempts without user explicit flag MUST be blocked
        res_blocked = vision_engine.analyze_screen("automatic check", is_user_explicit=False)
        self.assertIn("explicit user request", res_blocked)

    def test_screen_analysis_execution_and_cleanup(self):
        res = self.brain.process_command("JARVIS, analyze my screen.")
        self.assertTrue(res.success)
        self.assertEqual(res.intent, "vision_screen_analysis")

    def test_visual_reference_resolution(self):
        self.brain.process_command("JARVIS, analyze my screen.")
        res_ref = self.brain.process_command("Read that error.")
        self.assertTrue(res_ref.success)
        self.assertTrue(len(res_ref.text) > 0)

if __name__ == "__main__":
    unittest.main()
