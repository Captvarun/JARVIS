import unittest
from core.brain.intent import IntentDetector, IntentCategory
from core.brain.brain import JarvisBrain
from engine.vision.vision_engine import vision_engine

class TestMilestone6VisionEnginePatch2(unittest.TestCase):
    def setUp(self):
        self.brain = JarvisBrain()
        self.brain.initialize()
        self.brain.context.reset_memory()

    def test_a_fresh_start_implicit_visual_query(self):
        # TEST A: Fresh start -> "What am I seeing?" -> VISION_SCREEN_ANALYSIS without prior context
        res = self.brain.process_command("What am I seeing?")
        self.assertTrue(res.success)
        self.assertEqual(res.intent, "vision_screen_analysis")

    def test_b_analyze_my_screen(self):
        # TEST B: "Analyze my screen." -> VISION_SCREEN_ANALYSIS
        res = self.brain.process_command("Analyze my screen.")
        self.assertTrue(res.success)
        self.assertEqual(res.intent, "vision_screen_analysis")

    def test_c_what_else_am_i_doing(self):
        self.brain.process_command("Analyze my screen.")
        # TEST C: "What else am I doing?" -> VISION_SCREEN_ANALYSIS
        res = self.brain.process_command("What else am I doing?")
        self.assertTrue(res.success)
        self.assertEqual(res.intent, "vision_screen_analysis")

    def test_d_can_you_see_my_code(self):
        # TEST D: "Can you see my code?" -> VISION_SCREEN_ANALYSIS
        res = self.brain.process_command("Can you see my code?")
        self.assertTrue(res.success)
        self.assertEqual(res.intent, "vision_screen_analysis")

    def test_e_what_was_the_thing_you_saw_earlier(self):
        self.brain.process_command("Analyze my screen.")
        # TEST E: "What was the thing you saw earlier?" -> Previous visual context (Current screen required: NO)
        res = self.brain.process_command("What was the thing you saw earlier?")
        self.assertTrue(res.success)
        self.assertEqual(res.intent, "vision_screen_analysis")
        self.assertIn("previous screen analysis", res.text.lower())

    def test_f_whats_on_my_screen_right_now(self):
        self.brain.process_command("Analyze my screen.")
        # TEST F: "What's on my screen right now?" -> VISION_SCREEN_ANALYSIS (Current screen required: YES)
        res = self.brain.process_command("What's on my screen right now?")
        self.assertTrue(res.success)
        self.assertEqual(res.intent, "vision_screen_analysis")

    def test_g_did_anything_change(self):
        self.brain.process_command("Analyze my screen.")
        # TEST G: "Did anything change?" -> VISION_SCREEN_ANALYSIS (Current screen required: YES)
        res = self.brain.process_command("Did anything change?")
        self.assertTrue(res.success)
        self.assertEqual(res.intent, "vision_screen_analysis")

    def test_h_i_j_non_vision_conversational_queries(self):
        self.brain.process_command("Analyze my screen.")

        # TEST H: "Tell me a joke." -> conversation
        res_h = self.brain.process_command("Tell me a joke.")
        self.assertNotEqual(res_h.intent, "vision_screen_analysis")

        # TEST I: "How are you?" -> conversation
        res_i = self.brain.process_command("How are you?")
        self.assertNotEqual(res_i.intent, "vision_screen_analysis")

        # TEST J: "What's wrong with my life?" -> conversation
        res_j = self.brain.process_command("What's wrong with my life?")
        self.assertNotEqual(res_j.intent, "vision_screen_analysis")

    def test_overmatching_prevention(self):
        # Queries containing "what", "see", "think" that are NOT visual screen requests
        detector = IntentDetector()
        self.assertNotEqual(detector.detect("What do you think about my project?"), IntentCategory.VISION_SCREEN_ANALYSIS)
        self.assertNotEqual(detector.detect("Do you see what I mean?"), IntentCategory.VISION_SCREEN_ANALYSIS)

if __name__ == "__main__":
    unittest.main()
