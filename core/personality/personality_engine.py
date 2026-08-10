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
    Implements Contextual Humor Engine with explicit Response Mode determination and logging.
    """
    def __init__(self):
        self.state = PersonalityState()
        self.parser = PersonalityParser()
        self.context_mgr = PersonalityContextManager()

        self.turn_count: int = 0
        self.turns_since_humor: int = 10
        self.turns_since_sarcasm: int = 10
        self.recent_phrases_history: List[str] = []

    def process_command(self, prompt: str) -> str:
        """Parses and executes a natural language personality command."""
        parsed = self.parser.parse(prompt)
        cmd_type = parsed.get("type")

        # 1. Personality Query
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

        # 4. Temporary Overrides
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

        # 5. Parameter Modifications
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
        Evaluates context, humor/sarcasm eligibility, computes explicit Response Mode,
        emits Requirement 12 debug logs, and transforms response phrasing.
        """
        if not text:
            return text

        self.turn_count += 1
        self.turns_since_humor += 1
        self.turns_since_sarcasm += 1

        # 1. Classify Context
        context = self.context_mgr.classify_interaction(text, intent_str)
        params = self.state.get_all_params()
        humor_lvl = params.get("humor", 65)
        sarcasm_lvl = params.get("sarcasm", 30)

        # 2. Evaluate Decision Engine & Response Mode
        humor_ok = self.context_mgr.evaluate_humor_decision(context, humor_lvl, self.turns_since_humor)
        sarcasm_ok = self.context_mgr.evaluate_sarcasm_decision(context, sarcasm_lvl, self.turns_since_sarcasm)
        response_mode = self.context_mgr.determine_response_mode(context, humor_ok, sarcasm_ok)

        humor_dec_str = "ENABLED" if humor_ok else "SUPPRESSED"
        sarcasm_dec_str = "ENABLED" if sarcasm_ok else "SUPPRESSED"

        # 3. Emit Requirement 12 Structured Debug Logs
        events.log_emitted.emit("personality", f"Profile: {self.state.active_profile} | Humor: {humor_lvl}% | Sarcasm: {sarcasm_lvl}%")
        events.log_emitted.emit("personality", f"Context: {context}")
        events.log_emitted.emit("personality", f"Humor decision: {humor_dec_str}")
        events.log_emitted.emit("personality", f"Sarcasm decision: {sarcasm_dec_str}")
        events.log_emitted.emit("personality", f"Response mode: {response_mode}")
        events.log_emitted.emit("personality", "Response generation: CONTEXTUAL")

        res = text.strip()

        # Apply phrasing variation based on Response Mode
        if context == "GREETING" and (humor_ok or sarcasm_ok):
            greetings = [
                "Hey, Varun. Ready when you are.",
                "Good day, Varun. All systems operational.",
                "Greetings, Varun. How can I assist you today?"
            ]
            res = random.choice(greetings)
            self.turns_since_humor = 0

        return res

# Global Personality Engine Singleton
personality_engine = PersonalityEngine()
