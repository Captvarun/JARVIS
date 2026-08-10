from typing import Dict, Any, Optional
from core.personality.personality_state import PersonalityState
from core.personality.personality_parser import PersonalityParser
from core.personality.personality_context import PersonalityContextManager
from core.events import events
from core.logger import logger

class PersonalityEngine:
    """
    JARVIS Adaptive Personality & Behavior Coordinator.
    Handles command parsing, state updates, SQLite persistence, context awareness,
    and Response Transformation (modifying actual output phrasing based on personality).
    """
    def __init__(self):
        self.state = PersonalityState()
        self.parser = PersonalityParser()
        self.context_mgr = PersonalityContextManager()

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
            return "Understood. Personality state reset to default COMPANION profile."

        # 3. Profile Switching
        if cmd_type == "SET_PERSONALITY_PROFILE":
            prof = parsed.get("profile")
            if prof and self.state.set_profile(prof):
                events.log_emitted.emit("personality", f"Applied profile preset: {prof}")
                return f"Switched to {prof} mode."

        # 4. Temporary Conversational Overrides
        if cmd_type == "TEMP_OVERRIDE":
            override_type = parsed.get("override_type")
            if override_type == "SERIOUS":
                self.context_mgr.set_temp_override("suppress_humor", True)
                self.context_mgr.set_temp_override("suppress_sarcasm", True)
                events.log_emitted.emit("personality", "Temporary context override: SERIOUS (Humor & Sarcasm suppressed)")
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
                return f"{param.capitalize()} updated to {new_val}%."

        return f"Personality updated. Current Profile: {self.state.active_profile}."

    def transform_response(self, text: str, context_tag: str = "NORMAL") -> str:
        """
        Applies Personality Response Transformation to AI output text.
        Modifies phrasing, tone, verbosity, formality, humor, sarcasm, and friendliness.
        """
        if not text:
            return text

        self.context_mgr.set_context(context_tag)
        base_params = self.state.get_all_params()
        params = self.context_mgr.get_effective_params(base_params)

        res = text.strip()

        # 1. Formality Transformations
        formality = params.get("formality", 35)
        if formality >= 75:
            if res.startswith("Hello"):
                res = res.replace("Hello", "Greetings")
            elif res.startswith("Got it") or res.startswith("Done"):
                res = "Understood. " + res
        elif formality <= 25:
            if "I am JARVIS" in res:
                res = res.replace("I am JARVIS", "I'm JARVIS")
            if "Systems are operational." in res:
                res = res.replace("Systems are operational.", "All systems good to go.")
            elif "Systems are operational" in res:
                res = res.replace("Systems are operational", "All systems good to go")

        # 2. Verbosity Transformations
        verbosity = params.get("verbosity", 55)
        if verbosity <= 25:
            # Concise: shorten response if lengthy
            sentences = res.split(". ")
            if len(sentences) > 1:
                res = sentences[0] + "."
        elif verbosity >= 80:
            # Verbose: append detailed context if brief
            if not res.endswith("."):
                res += "."
            res += " All subsystem status checks remain nominal."

        # 3. Sarcasm & Humor Transformations (only if not suppressed by context)
        sarcasm = params.get("sarcasm", 30)
        humor = params.get("humor", 65)

        if sarcasm >= 75:
            if "operational" in res.lower() or "systems" in res.lower() or "go" in res.lower():
                if not res.endswith("."):
                    res += "."
                res += " Shockingly, nothing has caught fire yet."
        elif humor >= 75 and sarcasm < 75:
            if "operational" in res.lower() or "systems" in res.lower():
                if not res.endswith("."):
                    res += "."
                res += " Machine gods are pleased."

        # 4. Friendliness & Empathy Transformations
        friendliness = params.get("friendliness", 80)
        if friendliness >= 85 and not res.startswith("Hello") and not res.startswith("Greetings") and formality < 75:
            if not res.startswith("Sure thing"):
                res = f"Sure thing. {res}"

        return res

    def get_llm_context(self) -> Dict[str, Any]:
        """Exposes clean JSON/dict representation for future LLM integration."""
        return {
            "active_profile": self.state.active_profile,
            "parameters": self.state.get_all_params(),
            "context_tag": self.context_mgr.context_tag,
            "temp_overrides": self.context_mgr.temp_overrides.copy()
        }

# Global Personality Engine Singleton
personality_engine = PersonalityEngine()
