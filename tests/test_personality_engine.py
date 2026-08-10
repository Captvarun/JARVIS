import unittest
from core.brain.intent import IntentDetector, IntentCategory
from core.personality.personality_engine import PersonalityEngine, personality_engine

class TestMilestone41ContextualHumorEngine(unittest.TestCase):
    def setUp(self):
        personality_engine.state.reset()
        personality_engine.context_mgr.clear_temp_overrides()

    def test_interaction_context_classification(self):
        ctx_mgr = personality_engine.context_mgr
        self.assertEqual(ctx_mgr.classify_interaction("Open Google", intent_str="plugin"), "SYSTEM_COMMAND")
        self.assertEqual(ctx_mgr.classify_interaction("What's my RAM usage?", intent_str="system_command"), "INFORMATION_REQUEST")
        self.assertEqual(ctx_mgr.classify_interaction("What is Python?", intent_str="conversation"), "TECHNICAL")
        self.assertEqual(ctx_mgr.classify_interaction("Jarvis roast me", intent_str="conversation"), "HUMOR_REQUEST")
        self.assertEqual(ctx_mgr.classify_interaction("I'm tired", intent_str="conversation"), "EMOTIONAL")
        self.assertEqual(ctx_mgr.classify_interaction("Hello Jarvis", intent_str="conversation"), "GREETING")

    def test_humor_sarcasm_suppression_for_information_and_technical_requests(self):
        ctx_mgr = personality_engine.context_mgr
        
        # Information requests (RAM usage, Python) must SUPPRESS humor & sarcasm
        self.assertFalse(ctx_mgr.evaluate_humor_decision("INFORMATION_REQUEST", 80, 5))
        self.assertFalse(ctx_mgr.evaluate_sarcasm_decision("INFORMATION_REQUEST", 80, 5))

        self.assertFalse(ctx_mgr.evaluate_humor_decision("TECHNICAL", 80, 5))
        self.assertFalse(ctx_mgr.evaluate_sarcasm_decision("TECHNICAL", 80, 5))

        self.assertFalse(ctx_mgr.evaluate_humor_decision("SYSTEM_COMMAND", 80, 5))
        self.assertFalse(ctx_mgr.evaluate_sarcasm_decision("SYSTEM_COMMAND", 80, 5))

    def test_humor_request_enabled(self):
        ctx_mgr = personality_engine.context_mgr
        self.assertTrue(ctx_mgr.evaluate_humor_decision("HUMOR_REQUEST", 65, 5))
        self.assertTrue(ctx_mgr.evaluate_sarcasm_decision("HUMOR_REQUEST", 30, 5))

    def test_personality_query_direct_and_suppressed(self):
        res = personality_engine.process_command("What's your sarcasm level?")
        self.assertIn("30%", res)

        res_set = personality_engine.process_command("Set your humor level to 80%")
        self.assertIn("80%", res_set)
        self.assertEqual(personality_engine.state.get("humor"), 80)

if __name__ == "__main__":
    unittest.main()
