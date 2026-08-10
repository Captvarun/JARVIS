import random
from typing import Dict, Any, Optional

class PersonalityContextManager:
    """
    Context Classifier & Behavioral Decision Engine for Milestone 4.1.
    Classifies interaction types into:
    SYSTEM_COMMAND, INFORMATION_REQUEST, CASUAL_CONVERSATION, GREETING,
    HUMOR_REQUEST, EMOTIONAL, TECHNICAL, REPEATED_QUERY, UNKNOWN.
    """
    def __init__(self):
        self.context_tag: str = "UNKNOWN"
        self.last_prompt: str = ""
        self.temp_overrides: Dict[str, Any] = {}

    def classify_interaction(self, prompt: str, intent_str: str = "conversation") -> str:
        """Classifies interaction into exact Milestone 4.1 categories."""
        p_lower = prompt.lower().strip()

        # Check for Repeated Query
        if p_lower == self.last_prompt and p_lower:
            self.context_tag = "REPEATED_QUERY"
            return self.context_tag
        self.last_prompt = p_lower

        # 1. Explicit Humor / Roast Requests
        if any(w in p_lower for w in ["roast me", "tell me a joke", "say something funny", "make me laugh"]):
            self.context_tag = "HUMOR_REQUEST"
            return self.context_tag

        # 2. Operational / System Commands
        if intent_str in ("plugin", "application_action") or any(w in p_lower for w in ["open google", "search web", "launch"]):
            self.context_tag = "SYSTEM_COMMAND"
            return self.context_tag

        # 3. Technical Knowledge Queries
        if any(w in p_lower for w in ["what is python", "explain python", "how does python work", "define ", "code"]):
            self.context_tag = "TECHNICAL"
            return self.context_tag

        # 4. System Telemetry & Factual Information Requests
        if intent_str in ("system_command", "information_request", "get_time") or any(w in p_lower for w in ["ram usage", "cpu usage", "system status", "disk", "uptime", "clock", "what time"]):
            self.context_tag = "INFORMATION_REQUEST"
            return self.context_tag

        # 5. Emotional / Serious Inputs
        if any(w in p_lower for w in ["tired", "exhausted", "stressed", "sad", "unhappy", "depressed", "emergency", "hurt"]):
            self.context_tag = "EMOTIONAL"
            return self.context_tag

        # 6. Greetings
        if any(w in p_lower for w in ["hello", "hi", "hey", "good morning", "good evening", "greetings"]):
            self.context_tag = "GREETING"
            return self.context_tag

        # 7. Personality Query / Management
        if any(w in p_lower for w in ["sarcasm level", "humor level", "personality", "settings"]):
            self.context_tag = "INFORMATION_REQUEST"
            return self.context_tag

        # 8. Casual Conversation
        if intent_str == "conversation":
            self.context_tag = "CASUAL_CONVERSATION"
            return self.context_tag

        self.context_tag = "UNKNOWN"
        return self.context_tag

    def evaluate_humor_decision(self, context: str, humor_level: int, turns_since_last: int) -> bool:
        """
        Determines humor decision: ENABLED or SUPPRESSED.
        Humor is SUPPRESSED for SYSTEM_COMMAND, TECHNICAL, INFORMATION_REQUEST, EMOTIONAL.
        """
        if context in ("SYSTEM_COMMAND", "TECHNICAL", "INFORMATION_REQUEST", "EMOTIONAL"):
            return False

        if "suppress_humor" in self.temp_overrides and self.temp_overrides["suppress_humor"]:
            return False

        if context == "HUMOR_REQUEST":
            return True

        if humor_level <= 0:
            return False

        # Probabilistic decision based on humor level %
        prob = (humor_level / 100.0) * 0.5
        return random.random() < prob

    def evaluate_sarcasm_decision(self, context: str, sarcasm_level: int, turns_since_last: int) -> bool:
        """
        Determines sarcasm decision: ENABLED or SUPPRESSED.
        Evaluated independently from humor.
        """
        if context in ("SYSTEM_COMMAND", "TECHNICAL", "INFORMATION_REQUEST", "EMOTIONAL"):
            return False

        if "suppress_sarcasm" in self.temp_overrides and self.temp_overrides["suppress_sarcasm"]:
            return False

        if context == "HUMOR_REQUEST" and sarcasm_level > 10:
            return True

        if sarcasm_level <= 0:
            return False

        prob = (sarcasm_level / 100.0) * 0.4
        return random.random() < prob

    def set_temp_override(self, param: str, val: Any):
        self.temp_overrides[param.lower()] = val

    def clear_temp_overrides(self):
        self.temp_overrides.clear()
        self.context_tag = "UNKNOWN"
