import random
from typing import Dict, Any, Optional

class PersonalityContextManager:
    """
    Context Classifier & Eligibility Decision Engine.
    Determines situation context (GREETING, CASUAL_CONVERSATION, SYSTEM_STATUS, PERSONALITY_MANAGEMENT, SERIOUS, CRITICAL)
    and enforces strict humor/sarcasm eligibility rules, temporary overrides, and context suppression.
    """
    def __init__(self):
        self.context_tag: str = "NORMAL"
        self.temp_overrides: Dict[str, Any] = {}

    def classify_context(self, prompt: str, intent_str: str) -> str:
        """Classifies prompt and intent into precise situational contexts."""
        p_lower = prompt.lower().strip()

        # 1. Personality Management & Queries (Zero Jokes Rule)
        if any(tag in intent_str for tag in ["personality", "get_personality", "modify_personality", "set_personality"]):
            self.context_tag = "PERSONALITY_MANAGEMENT"
            return self.context_tag

        # 2. Serious, Emotional, Security, or Emergency Contexts
        if any(w in p_lower for w in ["crash", "error", "fault", "failed", "died", "broken", "sad", "die", "emergency", "help", "serious", "bad"]):
            self.context_tag = "SERIOUS"
            return self.context_tag

        # 3. Explicit Joke Request
        if "tell me a joke" in p_lower or "say something funny" in p_lower:
            self.context_tag = "JOKE_REQUEST"
            return self.context_tag

        # 4. Greetings & Casual Small Talk
        if any(w in p_lower for w in ["hello", "hi", "hey", "good morning", "good evening", "greetings", "howdy"]):
            self.context_tag = "GREETING"
            return self.context_tag

        # 5. System Commands & Technical Status
        if any(w in p_lower for w in ["system status", "cpu", "ram", "disk", "uptime", "telemetry", "specs", "open google", "search"]):
            self.context_tag = "SYSTEM_STATUS"
            return self.context_tag

        # 6. Informational Queries
        if any(w in p_lower for w in ["what time", "clock", "date", "my project"]):
            self.context_tag = "INFORMATIONAL"
            return self.context_tag

        self.context_tag = "CASUAL_CONVERSATION"
        return self.context_tag

    def set_temp_override(self, param: str, val: Any):
        """Sets temporary conversational override for current session."""
        self.temp_overrides[param.lower()] = val

    def clear_temp_overrides(self):
        """Clears temporary conversational overrides."""
        self.temp_overrides.clear()
        self.context_tag = "NORMAL"

    def should_allow_humor(self, context: str, humor_level: int, turns_since_last: int) -> bool:
        """
        Calculates humor eligibility based on context, level, and turns since last humor.
        Never injects random jokes into Personality Queries, System Commands, or Serious contexts.
        """
        if context in ("PERSONALITY_MANAGEMENT", "SYSTEM_STATUS", "INFORMATIONAL", "SERIOUS", "CRITICAL", "ERROR"):
            return False

        if "suppress_humor" in self.temp_overrides and self.temp_overrides["suppress_humor"]:
            return False

        if context == "JOKE_REQUEST":
            return True

        if humor_level <= 10:
            return False

        # Enforce cooldown: require at least 2 turns between humor remarks
        if turns_since_last < 2:
            return False

        # Eligibility threshold
        prob = (humor_level / 100.0) * 0.4
        return random.random() < prob

    def should_allow_sarcasm(self, context: str, sarcasm_level: int, turns_since_last: int) -> bool:
        """
        Calculates sarcasm eligibility.
        Sarcasm is highly selective and reserved ONLY for casual greetings or explicit small talk.
        """
        if context not in ("GREETING", "CASUAL_CONVERSATION", "SMALL_TALK"):
            return False

        if "suppress_sarcasm" in self.temp_overrides and self.temp_overrides["suppress_sarcasm"]:
            return False

        if sarcasm_level <= 20:
            return False

        # Enforce cooldown: require at least 3 turns between sarcasm remarks
        if turns_since_last < 3:
            return False

        prob = (sarcasm_level / 100.0) * 0.3
        return random.random() < prob

    def get_effective_params(self, base_params: Dict[str, int]) -> Dict[str, int]:
        """Computes effective runtime parameters considering context suppression."""
        effective = base_params.copy()

        if self.context_tag in ("SERIOUS", "DISTRESS", "SYSTEM_ERROR", "CRITICAL", "PERSONALITY_MANAGEMENT"):
            effective["humor"] = min(effective["humor"], 5)
            effective["sarcasm"] = 0

        if "suppress_humor" in self.temp_overrides and self.temp_overrides["suppress_humor"]:
            effective["humor"] = 0
        if "suppress_sarcasm" in self.temp_overrides and self.temp_overrides["suppress_sarcasm"]:
            effective["sarcasm"] = 0

        return effective
