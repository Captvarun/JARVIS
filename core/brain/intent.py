from enum import Enum

class IntentCategory(Enum):
    CONVERSATION = "conversation"
    SYSTEM_COMMAND = "system_command"
    INFORMATION_REQUEST = "information_request"
    APPLICATION_ACTION = "application_action"
    MEMORY = "memory"
    PLUGIN = "plugin"
    UNKNOWN = "unknown"

class IntentDetector:
    """
    Analyzes natural-language input to classify intent.
    """
    def detect(self, prompt: str) -> IntentCategory:
        p = prompt.lower().strip()

        if not p:
            return IntentCategory.UNKNOWN

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
