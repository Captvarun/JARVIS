import unittest
from core.brain.intent import IntentDetector, IntentCategory
from core.brain.brain import JarvisBrain
from engine.vision.vision_engine import vision_engine

class TestMilestone6VisionEnginePatch(unittest.TestCase):
    def setUp(self):
        self.brain = JarvisBrain()
        self.brain.initialize()
        self.brain.context.reset_memory()

    def test_explicit_and_implicit_vision_intent_detection(self):
        detector = IntentDetector()
        
        # Explicit commands without prior context
        explicit_prompts = [
            "JARVIS, analyze my screen.",
            "Describe the important things you can see on my screen",
            "Can you see my code?",
            "what am I looking at?",
            "look at my screen",
            "what's on my screen?",
            "read my screen",
            "inspect my screen"
        ]
        for p in explicit_prompts:
            self.assertEqual(
                detector.detect(p, context_mgr=self.brain.context), 
                IntentCategory.VISION_SCREEN_ANALYSIS, 
                f"Explicit prompt failed: {p}"
            )

    def test_contextual_visual_followups_sequence(self):
        # 1. "Analyze my screen." -> Vision
        res1 = self.brain.process_command("Analyze my screen.")
        self.assertTrue(res1.success)
        self.assertEqual(res1.intent, "vision_screen_analysis")

        # 2. "What else am I doing?" -> Contextual Vision
        res2 = self.brain.process_command("What else am I doing?")
        self.assertTrue(res2.success)
        self.assertEqual(res2.intent, "vision_screen_analysis")

        # 3. "Can you see my code?" -> Contextual Vision
        res3 = self.brain.process_command("Can you see my code?")
        self.assertTrue(res3.success)
        self.assertEqual(res3.intent, "vision_screen_analysis")

        # 4. "What error do you see?" -> Vision
        res4 = self.brain.process_command("What error do you see?")
        self.assertTrue(res4.success)
        self.assertEqual(res4.intent, "vision_screen_analysis")

        # 5. "What was the error you saw?" -> Previous visual context without new capture
        res5 = self.brain.process_command("What was the error you saw?")
        self.assertTrue(res5.success)
        self.assertEqual(res5.intent, "vision_screen_analysis")
        self.assertIn("previous screen analysis", res5.text.lower())

        # 6. "What's on my screen now?" -> New ONE_SHOT capture
        res6 = self.brain.process_command("What's on my screen now?")
        self.assertTrue(res6.success)
        self.assertEqual(res6.intent, "vision_screen_analysis")

        # 7. "Did anything change?" -> New ONE_SHOT capture
        res7 = self.brain.process_command("Did anything change?")
        self.assertTrue(res7.success)
        self.assertEqual(res7.intent, "vision_screen_analysis")

    def test_non_vision_vague_questions_remain_conversation(self):
        # Initial visual context active
        self.brain.process_command("Analyze my screen.")

        # 8. "Tell me a joke." -> Conversation
        res8 = self.brain.process_command("Tell me a joke.")
        self.assertNotEqual(res8.intent, "vision_screen_analysis")

        # 9. "How are you?" -> Conversation
        res9 = self.brain.process_command("How are you?")
        self.assertNotEqual(res9.intent, "vision_screen_analysis")

        # 10. "What's wrong with my life?" -> Conversation
        res10 = self.brain.process_command("What's wrong with my life?")
        self.assertNotEqual(res10.intent, "vision_screen_analysis")

    def test_privacy_check_enforcement(self):
        # Background/automatic attempts without user explicit flag MUST be blocked
        res_blocked = vision_engine.analyze_screen("automatic check", is_user_explicit=False)
        self.assertIn("explicit user request", res_blocked)

if __name__ == "__main__":
    unittest.main()
