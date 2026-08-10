import unittest
from core.brain.intent import IntentDetector, IntentCategory
from core.personality.personality_engine import PersonalityEngine, personality_engine

class TestMilestone5RefinedPersonalityEngine(unittest.TestCase):
    def setUp(self):
        personality_engine.state.reset()
        personality_engine.context_mgr.clear_temp_overrides()
        personality_engine.recent_phrases_history.clear()

    def test_intent_priority_for_personality_queries(self):
        detector = IntentDetector()
        self.assertEqual(detector.detect("What is your sarcasm level?"), IntentCategory.GET_PERSONALITY)
        self.assertEqual(detector.detect("What is your humor level?"), IntentCategory.GET_PERSONALITY)
        self.assertEqual(detector.detect("How sarcastic are you?"), IntentCategory.GET_PERSONALITY)
        self.assertEqual(detector.detect("What's your personality?"), IntentCategory.GET_PERSONALITY)
        self.assertEqual(detector.detect("What are your current settings?"), IntentCategory.GET_PERSONALITY)

    def test_personality_query_direct_response(self):
        # Must return exact current level cleanly without generic jokes
        res = personality_engine.process_command("What is your sarcasm level?")
        self.assertIn("30%", res)
        self.assertNotIn("catch fire", res.lower())

    def test_personality_modification_direct_response(self):
        res = personality_engine.process_command("Set sarcasm to 30%")
        self.assertIn("30%", res)
        self.assertNotIn("catch fire", res.lower())

    def test_answer_first_zero_joke_contexts(self):
        # Factual system status & informational queries must not contain random jokes
        sys_res = personality_engine.transform_response("CPU utilization is currently 42%.", intent_str="system_command")
        self.assertEqual(sys_res, "CPU utilization is currently 42%.")

        time_res = personality_engine.transform_response("The current local time is 09:15 AM.", intent_str="information_request")
        self.assertEqual(time_res, "The current local time is 09:15 AM.")

    def test_novelty_and_varied_greetings(self):
        greetings = set()
        for _ in range(5):
            res = personality_engine.transform_response("Hey Jarvis", intent_str="conversation")
            greetings.add(res)

        # Must produce varied greetings without repeating any single hardcoded joke
        self.assertGreater(len(greetings), 1)
        for g in greetings:
            self.assertNotIn("nothing has caught fire", g.lower())

if __name__ == "__main__":
    unittest.main()
