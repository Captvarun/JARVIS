import unittest
from core.brain.intent import IntentDetector, IntentCategory
from core.brain.brain import JarvisBrain

class TestMilestone7to10VisionIntelligence(unittest.TestCase):
    def setUp(self):
        self.brain = JarvisBrain()
        self.brain.initialize()
        self.brain.context.reset_memory()

    def test_required_m7_m10_exact_sequence(self):
        # TEST 1: User: "Analyze my screen."
        res1 = self.brain.process_command("Analyze my screen.")
        self.assertTrue(res1.success)
        self.assertEqual(res1.intent, "vision_screen_analysis")
        self.assertIsNotNone(self.brain.context.active_visual_context)
        self.assertIsNone(self.brain.context.active_visual_context.get("raw_capture"))

        # TEST 2: User: "What application am I using?"
        res2 = self.brain.process_command("What application am I using?")
        self.assertTrue(res2.success)
        self.assertEqual(res2.intent, "vision_screen_analysis")
        self.assertIn("based on the previous screen analysis", res2.text.lower())

        # TEST 3: User: "What project am I working on?"
        res3 = self.brain.process_command("What project am I working on?")
        self.assertTrue(res3.success)
        self.assertEqual(res3.intent, "vision_screen_analysis")
        self.assertIn("based on the previous screen analysis", res3.text.lower())

        # TEST 4: User: "What else am I doing?"
        res4 = self.brain.process_command("What else am I doing?")
        self.assertTrue(res4.success)
        self.assertEqual(res4.intent, "vision_screen_analysis")

        # TEST 5: User: "Do you see any errors?"
        res5 = self.brain.process_command("Do you see any errors?")
        self.assertTrue(res5.success)
        self.assertEqual(res5.intent, "vision_screen_analysis")

        # TEST 6: User: "What did you see previously?"
        res6 = self.brain.process_command("What did you see previously?")
        self.assertTrue(res6.success)
        self.assertEqual(res6.intent, "vision_screen_analysis")
        self.assertIn("based on the previous screen analysis", res6.text.lower())

        # TEST 7: User: "What was that error?"
        res7 = self.brain.process_command("What was that error?")
        self.assertTrue(res7.success)
        self.assertEqual(res7.intent, "vision_screen_analysis")
        self.assertIn("based on the previous screen analysis", res7.text.lower())

        # TEST 8: User: "Is it still there?"
        res8 = self.brain.process_command("Is it still there?")
        self.assertTrue(res8.success)
        self.assertEqual(res8.intent, "vision_screen_analysis")
        self.assertNotIn("based on the previous screen analysis", res8.text.lower())

        # TEST 9: User: "Did anything change?"
        res9 = self.brain.process_command("Did anything change?")
        self.assertTrue(res9.success)
        self.assertEqual(res9.intent, "vision_screen_analysis")
        self.assertNotIn("based on the previous screen analysis", res9.text.lower())

        # TEST 10: User: "What's different now?"
        res10 = self.brain.process_command("What's different now?")
        self.assertTrue(res10.success)
        self.assertEqual(res10.intent, "vision_screen_analysis")

        # TEST 11: User: "Tell me a joke." -> conversation (NO Vision)
        res11 = self.brain.process_command("Tell me a joke.")
        self.assertNotEqual(res11.intent, "vision_screen_analysis")
        self.assertEqual(res11.intent, "conversation")

        # TEST 12: User: "How are you?" -> conversation (NO Vision)
        res12 = self.brain.process_command("How are you?")
        self.assertNotEqual(res12.intent, "vision_screen_analysis")
        self.assertEqual(res12.intent, "conversation")

        # TEST 13: User: "What's wrong with my life?" -> conversation (NO Vision)
        res13 = self.brain.process_command("What's wrong with my life?")
        self.assertNotEqual(res13.intent, "vision_screen_analysis")
        self.assertEqual(res13.intent, "conversation")

        # TEST 14: User: "What's on my screen now?"
        res14 = self.brain.process_command("What's on my screen now?")
        self.assertTrue(res14.success)
        self.assertEqual(res14.intent, "vision_screen_analysis")

    def test_spelling_normalization_and_privacy(self):
        detector = IntentDetector()
        self.assertEqual(detector.detect("Analyse my screen."), IntentCategory.VISION_SCREEN_ANALYSIS)
        self.assertEqual(detector.detect("Analyze my screen."), IntentCategory.VISION_SCREEN_ANALYSIS)

        # Confirm non-vision protection
        self.assertEqual(detector.detect("Tell me a story."), IntentCategory.CONVERSATION)
        self.assertEqual(detector.detect("Good morning."), IntentCategory.CONVERSATION)
        self.assertEqual(detector.detect("I'm bored."), IntentCategory.CONVERSATION)

if __name__ == "__main__":
    unittest.main()
