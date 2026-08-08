import unittest
from core.personality.personality import PersonalityState, personality
from core.personality.handler import PersonalityHandler

class TestPersonalityEngine(unittest.TestCase):
    def setUp(self):
        personality.reset()

    def test_default_values(self):
        self.assertEqual(personality.get("humor"), 65)
        self.assertEqual(personality.get("sarcasm"), 30)
        self.assertEqual(personality.get("empathy"), 85)
        self.assertEqual(personality.get("formality"), 35)

    def test_absolute_set_and_clamping(self):
        personality.set("sarcasm", 40)
        self.assertEqual(personality.get("sarcasm"), 40)
        self.assertEqual(personality.active_profile, "CUSTOM")

        # Clamping test
        personality.set("humor", 150)
        self.assertEqual(personality.get("humor"), 100)
        personality.set("humor", -20)
        self.assertEqual(personality.get("humor"), 0)

    def test_relative_modify(self):
        personality.set("sarcasm", 50)
        personality.modify("sarcasm", -20)
        self.assertEqual(personality.get("sarcasm"), 30)

    def test_profiles(self):
        self.assertTrue(personality.set_profile("PROFESSIONAL"))
        self.assertEqual(personality.get("sarcasm"), 0)
        self.assertEqual(personality.get("formality"), 90)
        self.assertEqual(personality.active_profile, "PROFESSIONAL")

        self.assertTrue(personality.set_profile("SARCASTIC"))
        self.assertEqual(personality.get("sarcasm"), 85)
        self.assertEqual(personality.active_profile, "SARCASTIC")

    def test_natural_language_handler(self):
        handler = PersonalityHandler()
        res1 = handler.handle_command("set sarcasm to 30%")
        self.assertIn("30%", res1)
        self.assertEqual(personality.get("sarcasm"), 30)

        res2 = handler.handle_command("be more humorous")
        self.assertIn("Humor adjusted", res2)

        res3 = handler.handle_command("switch to focus mode")
        self.assertIn("FOCUS mode", res3)
        self.assertEqual(personality.active_profile, "FOCUS")

    def test_context_aware_humor(self):
        personality.set("sarcasm", 50)
        personality.set("humor", 70)
        h, s = personality.get_effective_humor_and_sarcasm("SERIOUS")
        self.assertEqual(h, 0)
        self.assertEqual(s, 0)

        h_norm, s_norm = personality.get_effective_humor_and_sarcasm("NORMAL")
        self.assertEqual(h_norm, 70)
        self.assertEqual(s_norm, 50)

if __name__ == "__main__":
    unittest.main()
