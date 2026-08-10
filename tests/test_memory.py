import unittest
from core.brain.context import ContextManager
from core.brain.brain import JarvisBrain

class TestMilestone5ShortTermMemory(unittest.TestCase):
    def setUp(self):
        self.brain = JarvisBrain()
        self.brain.initialize()
        self.brain.context.reset_memory()

    def test_rolling_window_memory_bounding(self):
        ctx = ContextManager(max_turns=5)
        for i in range(10):
            ctx.add_turn(f"user msg {i}", f"jarvis resp {i}")
        self.assertEqual(len(ctx.history), 5)
        self.assertEqual(ctx.history[0]["user"], "user msg 5")

    def test_topic_tracking_and_transitions(self):
        ctx = self.brain.context
        
        self.brain.process_command("Tell me a joke")
        self.assertEqual(ctx.active_topic, "HUMOR")

        self.brain.process_command("What's my RAM usage?")
        self.assertEqual(ctx.active_topic, "SYSTEM")

        self.brain.process_command("What is Python?")
        self.assertEqual(ctx.active_topic, "TECHNICAL")

    def test_reference_resolution(self):
        ctx = self.brain.context
        
        # Test "it" resolution
        self.brain.process_command("What is Python?")
        res_it = self.brain.process_command("Why is it popular?")
        self.assertIn("Python is popular", res_it.text)

        # Test "that" resolution for RAM
        self.brain.process_command("What's my RAM usage?")
        res_that = self.brain.process_command("Is that bad?")
        self.assertIn("RAM", res_that.text)

    def test_memory_reset(self):
        ctx = self.brain.context
        self.brain.process_command("Tell me a joke")
        self.assertEqual(len(ctx.history), 1)

        res_reset = self.brain.process_command("Forget this conversation")
        self.assertEqual(len(ctx.history), 0)

        res_after = self.brain.process_command("What was the joke?")
        self.assertIn("reset", res_after.text.lower())

if __name__ == "__main__":
    unittest.main()
