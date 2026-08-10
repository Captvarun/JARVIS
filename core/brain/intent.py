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
    High-priority matching for Personality Queries and Modifications.
    """
    def detect(self, prompt: str) -> IntentCategory:
        p = prompt.lower().strip()

        if not p:
            return IntentCategory.UNKNOWN

        # 1. High-Priority Personality Queries (MUST match before generic conversation)
        if any(w in p for w in [
            "what's your personality", "what is your personality", "show your personality",
            "current settings", "current personality", "sarcasm level", "humor level",
            "empathy level", "formality level", "energy level", "verbosity level",
            "confidence level", "friendliness level", "how sarcastic are you",
            "how humorous are you", "how formal are you", "personality parameters",
            "personality settings"
        ]):
            return IntentCategory.GET_PERSONALITY

        # 2. Personality Reset
        if ("reset" in p and "personality" in p) or "default personality" in p:
            return IntentCategory.RESET_PERSONALITY

        # 3. Profile Switch
        if any(w in p for w in ["professional mode", "companion mode", "sarcastic mode", "focus mode", "switch to", "profile", "go into"]):
            return IntentCategory.SET_PERSONALITY_PROFILE

        # 4. Personality Parameter Modification & Tuning Commands
        if any(w in p for w in [
            "set ", "reduce ", "increase ", "make yourself ", "be more ", "be less ",
            "turn ", "stop being ", "calm down", "don't joke", "dont joke", "stop joking",
            "be serious", "keep it short", "explain in detail", "only joke occasionally"
        ]):
            if any(param in p for param in [
                "sarcasm", "humor", "formality", "empathy", "verbosity", "energy",
                "confidence", "friendliness", "formal", "funny", "humorous", "sarcastic",
                "friendly", "concise", "detailed", "serious", "witty", "joke"
            ]):
                return IntentCategory.MODIFY_PERSONALITY

        # 5. System Command Intent
        if any(w in p for w in ["system status", "cpu", "ram", "disk", "uptime", "os", "specs", "telemetry"]):
            return IntentCategory.SYSTEM_COMMAND

        # 6. Information Request Intent
        if any(w in p for w in ["what time", "current time", "date", "clock", "what is my name", "what can you do"]):
            return IntentCategory.INFORMATION_REQUEST

        # 7. Memory Query Intent
        if any(w in p for w in ["my project", "what is my project", "remember", "recall"]):
            return IntentCategory.MEMORY

        # 8. Plugin Intent
        if any(w in p for w in ["browser", "open google", "search", "youtube", "github", "spotify", "weather"]):
            return IntentCategory.PLUGIN

        # 9. General Conversation Intent
        if any(w in p for w in ["hello", "hi", "hey", "jarvis", "who are you", "what are you", "thank", "how are you"]):
            return IntentCategory.CONVERSATION

        return IntentCategory.CONVERSATION
