from enum import Enum

class IntentCategory(Enum):
    CONVERSATION = "conversation"
    SYSTEM_COMMAND = "system_command"
    INFORMATION_REQUEST = "information_request"
    APPLICATION_ACTION = "application_action"
    MEMORY = "memory"
    PLUGIN = "plugin"
    MODIFY_PERSONALITY = "modify_personality"
    GET_PERSONALITY = "get_personality"
    RESET_PERSONALITY = "reset_personality"
    SET_PERSONALITY_PROFILE = "set_personality_profile"
    UNKNOWN = "unknown"

class IntentDetector:
    """
    Analyzes natural-language input to classify intent.
    """
    def detect(self, prompt: str) -> IntentCategory:
        p = prompt.lower().strip()

        if not p:
            return IntentCategory.UNKNOWN

        # Personality Intents
        if any(w in p for w in ["what's your personality", "what is your personality", "show your personality", "current personality"]):
            return IntentCategory.GET_PERSONALITY

        if "reset" in p and "personality" in p:
            return IntentCategory.RESET_PERSONALITY

        if any(w in p for w in ["professional mode", "companion mode", "sarcastic mode", "focus mode", "switch to", "profile"]):
            return IntentCategory.SET_PERSONALITY_PROFILE

        if any(w in p for w in ["set ", "reduce ", "increase ", "make yourself ", "be more ", "be less ", "turn ", "sarcasm", "humor", "formality", "empathy", "verbosity"]):
            if any(param in p for param in ["sarcasm", "humor", "formality", "empathy", "verbosity", "energy", "confidence"]):
                return IntentCategory.MODIFY_PERSONALITY

        # System Command Intent
        if any(w in p for w in ["system status", "cpu", "ram", "disk", "uptime", "os", "specs", "telemetry"]):
            return IntentCategory.SYSTEM_COMMAND

        # Information Request Intent
        if any(w in p for w in ["what time", "current time", "date", "clock", "what is my name", "what can you do"]):
            return IntentCategory.INFORMATION_REQUEST

        # Memory Query Intent
        if any(w in p for w in ["my project", "what is my project", "remember", "recall"]):
            return IntentCategory.MEMORY

        # Plugin Intent
        if any(w in p for w in ["browser", "open google", "search", "youtube", "github", "spotify", "weather"]):
            return IntentCategory.PLUGIN

        # General Conversation Intent
        if any(w in p for w in ["hello", "hi", "hey", "jarvis", "who are you", "what are you", "thank", "how are you"]):
            return IntentCategory.CONVERSATION

        return IntentCategory.CONVERSATION
