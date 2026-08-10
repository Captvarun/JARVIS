import unittest
from core.personality.personality_engine import personality_engine

class TestMilestone4PersonalityEngineBugFix(unittest.TestCase):
    def setUp(self):
        personality_engine.state.reset()
        personality_engine.context_mgr.clear_temp_overrides()

    def test_semantic_intent_priority_over_repeated_query(self):
        ctx_mgr = personality_engine.context_mgr
        # First call
        ctx_1 = ctx_mgr.classify_interaction("humor me", intent_str="conversation")
        self.assertEqual(ctx_1, "HUMOR_REQUEST")

        # Second call (repeated exact prompt) MUST remain HUMOR_REQUEST
        ctx_2 = ctx_mgr.classify_interaction("humor me", intent_str="conversation")
        self.assertEqual(ctx_2, "HUMOR_REQUEST")

    def test_response_mode_determination(self):
        ctx_mgr = personality_engine.context_mgr

        # Information / System Command -> DIRECT / SYSTEM_OPERATIONAL
        mode_info = ctx_mgr.determine_response_mode("INFORMATION_REQUEST", False, False)
        self.assertEqual(mode_info, "DIRECT")

        mode_sys = ctx_mgr.determine_response_mode("SYSTEM_COMMAND", False, False)
        self.assertEqual(mode_sys, "SYSTEM_OPERATIONAL")

        # Emotional -> EMPATHETIC
        mode_emo = ctx_mgr.determine_response_mode("EMOTIONAL", False, False)
        self.assertEqual(mode_emo, "EMPATHETIC")

        # Humor Request + Humor Enabled + Sarcasm Enabled -> PLAYFUL_SARCASTIC
        mode_ps = ctx_mgr.determine_response_mode("HUMOR_REQUEST", True, True)
        self.assertEqual(mode_ps, "PLAYFUL_SARCASTIC")

        # Humor Request + Humor Enabled + Sarcasm Suppressed -> HUMOROUS
        mode_h = ctx_mgr.determine_response_mode("HUMOR_REQUEST", True, False)
        self.assertEqual(mode_h, "HUMOROUS")

        # Casual Conversation + Humor Enabled -> PLAYFUL
        mode_playful = ctx_mgr.determine_response_mode("CASUAL_CONVERSATION", True, False)
        self.assertEqual(mode_playful, "PLAYFUL")

if __name__ == "__main__":
    unittest.main()
