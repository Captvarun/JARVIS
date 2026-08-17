import unittest
from core.brain.intent import IntentDetector, IntentCategory
from core.brain.brain import JarvisBrain

class TestCompoundVisionReasoning(unittest.TestCase):
    def setUp(self):
        self.brain = JarvisBrain()
        self.brain.initialize()
        self.brain.context.reset_memory()

    def test_all_7_required_vision_tests(self):
        # 1. "Analyze my screen"
        res1 = self.brain.process_command("Analyze my screen")
        self.assertTrue(res1.success)
        self.assertEqual(res1.intent, "vision_screen_analysis")

        # 2. "What do you see?"
        res2 = self.brain.process_command("What do you see?")
        self.assertTrue(res2.success)
        self.assertEqual(res2.intent, "vision_screen_analysis")

        # 3. "What did you see previously?"
        res3 = self.brain.process_command("What did you see previously?")
        self.assertTrue(res3.success)
        self.assertEqual(res3.intent, "vision_screen_analysis")
        self.assertIn("based on the previous screen analysis", res3.text.lower())

        # 4. "Is it still there?"
        res4 = self.brain.process_command("Is it still there?")
        self.assertTrue(res4.success)
        self.assertEqual(res4.intent, "vision_screen_analysis")

        # 5. "What did you just see and what should I do next?" (Compound: Obs + Interp + Rec)
        res5 = self.brain.process_command("What did you just see and what should I do next?")
        self.assertTrue(res5.success)
        self.assertEqual(res5.intent, "vision_screen_analysis")
        self.assertIn("based on that", res5.text.lower())
        self.assertIn("your next step should be", res5.text.lower())

        # 6. "What's wrong with what you're seeing and how do I fix it?" (Compound: Obs + Interp + Rec)
        res6 = self.brain.process_command("What's wrong with what you're seeing and how do I fix it?")
        self.assertTrue(res6.success)
        self.assertEqual(res6.intent, "vision_screen_analysis")
        self.assertIn("based on that", res6.text.lower())
        self.assertIn("your next step should be", res6.text.lower())

        # 7. "Based on what you see, what's the next step?" (Compound: Obs + Interp + Rec)
        res7 = self.brain.process_command("Based on what you see, what's the next step?")
        self.assertTrue(res7.success)
        self.assertEqual(res7.intent, "vision_screen_analysis")
        self.assertIn("based on that", res7.text.lower())
        self.assertIn("your next step should be", res7.text.lower())

    def test_non_vision_protections(self):
        detector = IntentDetector()
        self.assertEqual(detector.detect("Tell me a joke."), IntentCategory.CONVERSATION)
        self.assertEqual(detector.detect("How are you?"), IntentCategory.CONVERSATION)

if __name__ == "__main__":
    unittest.main()
