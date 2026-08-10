import random
from typing import Dict, Any, Optional

class PersonalityContextManager:
    """
    Context Classifier & Behavioral Decision Engine for Milestone 4.
    Prioritizes semantic intent above REPEATED_QUERY and determines explicit Response Modes.
    """
    def __init__(self):
        self.context_tag: str = "UNKNOWN"
        self.last_prompt: str = ""
        self.temp_overrides: Dict[str, Any] = {}

    def classify_interaction(self, prompt: str, intent_str: str = "conversation") -> str:
        """
        Classifies interaction with semantic priority:
        1. HUMOR_REQUEST
        2. SYSTEM_COMMAND
        3. TECHNICAL
        4. INFORMATION_REQUEST
        5. EMOTIONAL
        6. GREETING
        7. CASUAL_CONVERSATION
        8. REPEATED_QUERY (only if unclassified above)
        9. UNKNOWN
        """
        p_lower = prompt.lower().strip()

        # 1. Explicit Humor / Roast Requests (HIGHEST PRIORITY)
        if any(w in p_lower for w in [
            "roast me", "roast", "tell me a joke", "joke", "humor me", 
            "make me laugh", "say something funny", "make me laugh jarvis"
        ]):
            self.context_tag = "HUMOR_REQUEST"
            self.last_prompt = p_lower
            return self.context_tag

        # 2. Operational / System Commands
        if intent_str in ("plugin", "application_action") or any(w in p_lower for w in ["open google", "search web", "launch"]):
            self.context_tag = "SYSTEM_COMMAND"
            self.last_prompt = p_lower
            return self.context_tag

        # 3. Technical Knowledge Queries
        if any(w in p_lower for w in ["what is python", "explain python", "how does python work", "define ", "code"]):
            self.context_tag = "TECHNICAL"
            self.last_prompt = p_lower
            return self.context_tag

        # 4. System Telemetry & Factual Information Requests
        if intent_str in ("system_command", "information_request", "get_time") or any(w in p_lower for w in ["ram usage", "cpu usage", "system status", "disk", "uptime", "clock", "what time"]):
            self.context_tag = "INFORMATION_REQUEST"
            self.last_prompt = p_lower
            return self.context_tag

        # 5. Emotional / Serious Inputs
        if any(w in p_lower for w in ["tired", "exhausted", "stressed", "sad", "unhappy", "depressed", "emergency", "hurt"]):
            self.context_tag = "EMOTIONAL"
            self.last_prompt = p_lower
            return self.context_tag

        # 6. Greetings
        if any(w in p_lower for w in ["hello", "hi", "hey", "good morning", "good evening", "greetings"]):
            self.context_tag = "GREETING"
            self.last_prompt = p_lower
            return self.context_tag

        # 7. Personality Query / Management
        if any(w in p_lower for w in ["sarcasm level", "humor level", "personality", "settings"]):
            self.context_tag = "INFORMATION_REQUEST"
            self.last_prompt = p_lower
            return self.context_tag

        # 8. Check for Repeated Query ONLY for generic inputs
        if p_lower == self.last_prompt and p_lower:
            self.context_tag = "REPEATED_QUERY"
            return self.context_tag

        self.last_prompt = p_lower

        # 9. Casual Conversation
        if intent_str == "conversation":
            self.context_tag = "CASUAL_CONVERSATION"
            return self.context_tag

        self.context_tag = "UNKNOWN"
        return self.context_tag

    def evaluate_humor_decision(self, context: str, humor_level: int, turns_since_last: int) -> bool:
        """Determines humor decision: ENABLED or SUPPRESSED."""
        if context in ("SYSTEM_COMMAND", "TECHNICAL", "INFORMATION_REQUEST", "EMOTIONAL"):
            return False

        if "suppress_humor" in self.temp_overrides and self.temp_overrides["suppress_humor"]:
            return False

        if context == "HUMOR_REQUEST":
            return True

        if humor_level <= 0:
            return False

        prob = (humor_level / 100.0) * 0.6
        return random.random() < prob

    def evaluate_sarcasm_decision(self, context: str, sarcasm_level: int, turns_since_last: int) -> bool:
        """Determines sarcasm decision: ENABLED or SUPPRESSED."""
        if context in ("SYSTEM_COMMAND", "TECHNICAL", "INFORMATION_REQUEST", "EMOTIONAL"):
            return False

        if "suppress_sarcasm" in self.temp_overrides and self.temp_overrides["suppress_sarcasm"]:
            return False

        if context == "HUMOR_REQUEST" and sarcasm_level > 10:
            return True

        if sarcasm_level <= 0:
            return False

        prob = (sarcasm_level / 100.0) * 0.5
        return random.random() < prob

    def determine_response_mode(self, context: str, humor_ok: bool, sarcasm_ok: bool) -> str:
        """Computes explicit Response Mode based on Context, Humor, and Sarcasm decisions."""
        if context in ("SYSTEM_COMMAND", "INFORMATION_REQUEST", "TECHNICAL"):
            return "DIRECT" if context != "SYSTEM_COMMAND" else "SYSTEM_OPERATIONAL"

        if context == "EMOTIONAL":
            return "EMPATHETIC"

        if context == "HUMOR_REQUEST":
            if humor_ok and sarcasm_ok:
                return "PLAYFUL_SARCASTIC"
            elif humor_ok:
                return "HUMOROUS"
            elif sarcasm_ok:
                return "SARCASTIC"
            return "DIRECT"

        if context in ("CASUAL_CONVERSATION", "GREETING", "REPEATED_QUERY"):
            if humor_ok and sarcasm_ok:
                return "PLAYFUL_SARCASTIC"
            elif humor_ok:
                return "PLAYFUL"
            elif sarcasm_ok:
                return "SARCASTIC"
            return "DIRECT"

        return "DIRECT"

    def set_temp_override(self, param: str, val: Any):
        self.temp_overrides[param.lower()] = val

    def clear_temp_overrides(self):
        self.temp_overrides.clear()
        self.context_tag = "UNKNOWN"
