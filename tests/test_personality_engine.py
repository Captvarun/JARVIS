import unittest
from core.personality.personality_state import PersonalityState
from core.personality.personality_engine import PersonalityEngine, personality_engine
from core.personality.personality_profiles import PROFILES

class TestMilestone5PersonalityEngine(unittest.TestCase):
    def setUp(self):
        personality_engine.state.reset()
        personality_engine.context_mgr.clear_temp_overrides()

    def test_eight_parameters(self):
        state = personality_engine.state
        self.assertEqual(state.get("humor"), 65)
        self.assertEqual(state.get("sarcasm"), 30)
        self.assertEqual(state.get("empathy"), 85)
        self.assertEqual(state.get("formality"), 35)
        self.assertEqual(state.get("energy"), 70)
        self.assertEqual(state.get("verbosity"), 55)
        self.assertEqual(state.get("confidence"), 90)
        self.assertEqual(state.get("friendliness"), 80)

    def test_clamping(self):
        state = personality_engine.state
        state.set("sarcasm", 150)
        self.assertEqual(state.get("sarcasm"), 100)
        state.set("humor", -50)
        self.assertEqual(state.get("humor"), 0)

    def test_profiles(self):
        state = personality_engine.state
        self.assertTrue(state.set_profile("PROFESSIONAL"))
        self.assertEqual(state.get("formality"), 85)
        self.assertEqual(state.get("sarcasm"), 5)
        self.assertEqual(state.active_profile, "PROFESSIONAL")

        self.assertTrue(state.set_profile("SARCASTIC"))
        self.assertEqual(state.get("sarcasm"), 80)
        self.assertEqual(state.active_profile, "SARCASTIC")

        self.assertTrue(state.set_profile("FOCUS"))
        self.assertEqual(state.get("humor"), 5)
        self.assertEqual(state.get("sarcasm"), 0)

    def test_natural_language_parsing_and_execution(self):
        engine = personality_engine
        
        # Absolute set
        res1 = engine.process_command("set sarcasm to 30%")
        self.assertIn("30%", res1)
        self.assertEqual(engine.state.get("sarcasm"), 30)

        # Relative change
        res2 = engine.process_command("reduce sarcasm by 20%")
        self.assertEqual(engine.state.get("sarcasm"), 10)

        # Qualitative commands
        engine.process_command("be more humorous")
        self.assertEqual(engine.state.get("humor"), 85)

        engine.process_command("be more friendly")
        self.assertEqual(engine.state.get("friendliness"), 100)

        # Profile switch
        res3 = engine.process_command("switch to professional mode")
        self.assertIn("PROFESSIONAL", res3)
        self.assertEqual(engine.state.active_profile, "PROFESSIONAL")

    def test_response_transformation(self):
        engine = personality_engine

        # High formality
        engine.state.set_profile("PROFESSIONAL")
        transformed_formal = engine.transform_response("Hello, Varun. Systems are operational.")
        self.assertIn("Greetings", transformed_formal)

        # High sarcasm
        engine.state.set_profile("SARCASTIC")
        transformed_sarcastic = engine.transform_response("Systems are operational.")
        self.assertIn("caught fire", transformed_sarcastic.lower())

    def test_context_aware_suppression(self):
        engine = personality_engine
        engine.state.set_profile("SARCASTIC") # High sarcasm (80)

        # In SERIOUS context, sarcasm is suppressed to 0 without changing stored DB state
        transformed_serious = engine.transform_response("Systems are operational.", context_tag="SERIOUS")
        self.assertNotIn("caught fire", transformed_serious.lower())
        self.assertEqual(engine.state.get("sarcasm"), 80) # Database state preserved!

if __name__ == "__main__":
    unittest.main()
