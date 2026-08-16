import unittest
from core.brain.intent import IntentDetector, IntentCategory
from core.brain.brain import JarvisBrain
from engine.vision.vision_engine import vision_engine

class TestMilestone61Patch(unittest.TestCase):
    def setUp(self):
        self.brain = JarvisBrain()
        self.brain.initialize()
        self.brain.context.reset_memory()

    def test_milestone_61_exact_sequence(self):
        # TEST 1: Analyze my screen.
        res1 = self.brain.process_command("Analyze my screen.")
        self.assertTrue(res1.success)
        self.assertEqual(res1.intent, "vision_screen_analysis")

        # TEST 2: What else am I doing?
        res2 = self.brain.process_command("What else am I doing?")
        self.assertTrue(res2.success)
        self.assertEqual(res2.intent, "vision_screen_analysis")

        # TEST 3: What was the error?
        res3 = self.brain.process_command("What was the error?")
        self.assertTrue(res3.success)
        self.assertEqual(res3.intent, "vision_screen_analysis")
        self.assertIn("previous screen analysis", res3.text.lower())

        # TEST 4: Is it still there? (Current-State Question -> ONE_SHOT Capture)
        res4 = self.brain.process_command("Is it still there?")
        self.assertTrue(res4.success)
        self.assertEqual(res4.intent, "vision_screen_analysis")
        self.assertNotIn("based on the previous screen analysis", res4.text.lower())

        # TEST 5: Did it disappear? (Current-State Question -> ONE_SHOT Capture)
        res5 = self.brain.process_command("Did it disappear?")
        self.assertTrue(res5.success)
        self.assertEqual(res5.intent, "vision_screen_analysis")
        self.assertNotIn("based on the previous screen analysis", res5.text.lower())

        # TEST 6: What did you see previously? (Context Recall -> Current screen required: NO)
        res6 = self.brain.process_command("What did you see previously?")
        self.assertTrue(res6.success)
        self.assertEqual(res6.intent, "vision_screen_analysis")
        self.assertIn("previous screen analysis", res6.text.lower())

        # TEST 7: What's on my screen now? (Current-State Question -> ONE_SHOT Capture)
        res7 = self.brain.process_command("What's on my screen now?")
        self.assertTrue(res7.success)
        self.assertEqual(res7.intent, "vision_screen_analysis")

        # TEST 8: Tell me a joke. -> conversation
        res8 = self.brain.process_command("Tell me a joke.")
        self.assertNotEqual(res8.intent, "vision_screen_analysis")

        # TEST 9: What's wrong with my life? -> conversation
        res9 = self.brain.process_command("What's wrong with my life?")
        self.assertNotEqual(res9.intent, "vision_screen_analysis")

        # TEST 10: How are you? -> conversation
        res10 = self.brain.process_command("How are you?")
        self.assertNotEqual(res10.intent, "vision_screen_analysis")

    def test_privacy_and_vague_queries(self):
        detector = IntentDetector()
        self.assertEqual(detector.detect("How is it going?"), IntentCategory.CONVERSATION)
        self.assertEqual(detector.detect("Is it funny?"), IntentCategory.CONVERSATION)

if __name__ == "__main__":
    unittest.main()
