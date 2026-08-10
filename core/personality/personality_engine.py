import random
from typing import Dict, Any, List, Optional
from core.personality.personality_state import PersonalityState
from core.personality.personality_parser import PersonalityParser
from core.personality.personality_context import PersonalityContextManager
from core.events import events
from core.logger import logger

class PersonalityEngine:
    """
    JARVIS Adaptive Personality & Behavior Coordinator.
    Implements Context Classification, Frequency Cooldown, Novelty Memory,
    and Answer-First Phrasing Transformations without repetitive hardcoded jokes.
    """
    def __init__(self):
        self.state = PersonalityState()
        self.parser = PersonalityParser()
        self.context_mgr = PersonalityContextManager()

        # Conversation & Cooldown Counters
        self.turn_count: int = 0
        self.turns_since_humor: int = 10
        self.turns_since_sarcasm: int = 10

        # Novelty Phrase Memory (Bounded Window)
        self.recent_phrases_history: List[str] = []
        self.max_novelty_window: int = 20

    def process_command(self, prompt: str) -> str:
        """Parses and executes a natural language personality command."""
        parsed = self.parser.parse(prompt)
        cmd_type = parsed.get("type")

        # 1. Personality Query (Direct Answer First)
        if cmd_type == "GET_PERSONALITY":
            param = parsed.get("param")
            if param:
                val = self.state.get(param)
                events.log_emitted.emit("personality", f"Query parameter '{param}': {val}%")
                return f"My current {param} level is {val}%."
            events.log_emitted.emit("personality", "Querying full personality breakdown")
            return self.state.get_summary()

        # 2. Reset Personality
        if cmd_type == "RESET_PERSONALITY":
            self.state.reset()
            self.context_mgr.clear_temp_overrides()
            events.log_emitted.emit("personality", "Personality state reset to default COMPANION profile.")
            return "Done. Personality state reset to default COMPANION profile."

        # 3. Profile Switching
        if cmd_type == "SET_PERSONALITY_PROFILE":
            prof = parsed.get("profile")
            if prof and self.state.set_profile(prof):
                events.log_emitted.emit("personality", f"Applied profile preset: {prof}")
                return f"Done. Switched to {prof} mode."

        # 4. Temporary Conversational Overrides
        if cmd_type == "TEMP_OVERRIDE":
            override_type = parsed.get("override_type")
            if override_type == "SERIOUS":
                self.context_mgr.set_temp_override("suppress_humor", True)
                self.context_mgr.set_temp_override("suppress_sarcasm", True)
                events.log_emitted.emit("personality", "Temporary context override: SERIOUS")
                return "Understood. Operating in serious mode for this session."
            elif override_type == "CONCISE":
                self.context_mgr.set_temp_override("verbosity", 20)
                events.log_emitted.emit("personality", "Temporary context override: CONCISE")
                return "Understood. Keeping responses concise."
            elif override_type == "VERBOSE":
                self.context_mgr.set_temp_override("verbosity", 85)
                events.log_emitted.emit("personality", "Temporary context override: VERBOSE")
                return "Understood. Providing detailed explanations."

        # 5. Parameter Modifications (Absolute & Relative)
        if cmd_type == "MODIFY_PERSONALITY":
            param = parsed.get("param")
            mode = parsed.get("mode")
            val = parsed.get("val")

            if param and val is not None:
                old_val = self.state.get(param)
                if mode == "ABSOLUTE":
                    self.state.set(param, val)
                else:
                    self.state.modify(param, val)
                new_val = self.state.get(param)

                events.log_emitted.emit("personality", f"Modification detected: {param} {old_val}% -> {new_val}% (Profile: {self.state.active_profile})")
                return f"Done. {param.capitalize()} is now set to {new_val}%."

        return f"Done. Current Profile: {self.state.active_profile}."

    def transform_response(self, text: str, intent_str: str = "conversation") -> str:
        """
        Transforms response phrasing based on context classification, personality level,
        cooldown counters, and novelty memory.
        """
        if not text:
            return text

        self.turn_count += 1
        self.turns_since_humor += 1
        self.turns_since_sarcasm += 1

        # Classify context
        context = self.context_mgr.classify_context(text, intent_str)
        params = self.context_mgr.get_effective_params(self.state.get_all_params())

        res = text.strip()

        # Strict Zero-Joke contexts: Return direct, clean response immediately!
        if context in ("PERSONALITY_MANAGEMENT", "SYSTEM_STATUS", "INFORMATIONAL", "SERIOUS", "CRITICAL", "ERROR"):
            return res

        # Check Eligibility for Optional Conversational Flavoring
        allow_humor = self.context_mgr.should_allow_humor(context, params.get("humor", 65), self.turns_since_humor)
        allow_sarcasm = self.context_mgr.should_allow_sarcasm(context, params.get("sarcasm", 30), self.turns_since_sarcasm)

        # Varied Greeting Phrases Bank (No Repetition!)
        if context == "GREETING":
            greetings_bank = [
                "Hey, Varun. Good to hear from you.",
                "Hello, Varun. Systems are online and ready.",
                "Good day, Varun. All systems operational.",
                "Greetings, Varun. How can I assist you?",
                "Hey, Varun. Ready when you are."
            ]
            
            sarcastic_greetings = [
                "Good morning, Varun. Another day, another attempt to keep things running smoothly.",
                "Hey, Varun. Systems are online and behaving themselves for once.",
                "Hello, Varun. Machine components remain cooperative."
            ]

            if allow_sarcasm:
                chosen = self._select_novel_phrase(sarcastic_greetings)
                self.turns_since_sarcasm = 0
                return chosen
            else:
                chosen = self._select_novel_phrase(greetings_bank)
                return chosen

        # Handle Explicit Joke Requests
        if context == "JOKE_REQUEST":
            jokes_bank = [
                "Why do programmers prefer dark mode? Because light attracts bugs.",
                "There are 10 types of people in the world: those who understand binary, and those who don't.",
                "Hardware is the part of a computer that you can kick when the software crashes."
            ]
            chosen = self._select_novel_phrase(jokes_bank)
            self.turns_since_humor = 0
            return chosen

        return res

    def _select_novel_phrase(self, phrase_candidates: List[str]) -> str:
        """Selects a phrase candidate that has NOT been used recently."""
        available = [p for p in phrase_candidates if p not in self.recent_phrases_history]
        if not available:
            # Clear history if exhausted
            available = phrase_candidates

        chosen = random.choice(available)
        self.recent_phrases_history.append(chosen)

        # Keep sliding novelty window capped at max_novelty_window
        if len(self.recent_phrases_history) > self.max_novelty_window:
            self.recent_phrases_history.pop(0)

        return chosen

    def get_llm_context(self) -> Dict[str, Any]:
        """Exposes clean representation for future LLM integration."""
        return {
            "active_profile": self.state.active_profile,
            "parameters": self.state.get_all_params(),
            "context_tag": self.context_mgr.context_tag,
            "turns_since_humor": self.turns_since_humor,
            "turns_since_sarcasm": self.turns_since_sarcasm
        }

# Global Personality Engine Singleton
personality_engine = PersonalityEngine()
