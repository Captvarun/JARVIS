import time
from typing import List, Dict, Any, Optional
from core.events import events
from core.logger import logger

class ContextManager:
    """
    Short-Term Conversational Memory & Reference Resolution Engine for Milestone 5.
    Maintains a bounded rolling window of structured turns, active topic tracking,
    pronoun/anaphora reference resolution, and memory reset.
    """
    def __init__(self, max_turns: int = 15):
        self.max_turns = max_turns
        self.history: List[Dict[str, Any]] = []
        self.active_topic: str = "UNKNOWN"
        events.log_emitted.emit("conversation", "Memory initialized")

    def add_turn(
        self, 
        user_msg: str, 
        jarvis_resp: str, 
        intent: str = "conversation", 
        context: str = "CASUAL_CONVERSATION", 
        response_mode: str = "DIRECT"
    ):
        """Adds a full structured interaction turn to rolling memory."""
        topic = self.classify_topic(intent, context, user_msg)
        self.active_topic = topic

        turn = {
            "user": user_msg,
            "assistant": jarvis_resp,
            "intent": intent,
            "context": context,
            "topic": topic,
            "response_mode": response_mode,
            "timestamp": time.time()
        }

        self.history.append(turn)

        # Enforce rolling window bound
        if len(self.history) > self.max_turns:
            self.history.pop(0)

        events.log_emitted.emit("conversation", f"Active topic: {self.active_topic} | Memory size: {len(self.history)} turns")

    def classify_topic(self, intent: str, context: str, user_msg: str) -> str:
        """Determines active topic from intent, context, and input keywords."""
        p_lower = user_msg.lower().strip()

        if context == "HUMOR_REQUEST" or any(w in p_lower for w in ["joke", "roast", "funny", "humor"]):
            return "HUMOR"
        if context == "TECHNICAL" or "python" in p_lower or "code" in p_lower:
            return "TECHNICAL"
        if context in ("SYSTEM_COMMAND", "INFORMATION_REQUEST") or any(w in p_lower for w in ["ram", "cpu", "disk", "status", "system"]):
            return "SYSTEM"
        if context == "EMOTIONAL" or any(w in p_lower for w in ["tired", "stressed"]):
            return "EMOTIONAL"
        if "sarcasm" in p_lower or "humor level" in p_lower or "personality" in p_lower:
            return "PERSONALITY"
        if context == "GREETING" or context == "CASUAL_CONVERSATION":
            return "CASUAL"

        return self.active_topic if self.active_topic != "UNKNOWN" else "GENERAL_INFORMATION"

    def resolve_references(self, prompt: str) -> Dict[str, Any]:
        """
        Lightweight Reference Resolution Engine.
        Resolves pronouns ('it', 'that'), follow-ups ('another one', 'why'), and ambiguous state questions.
        """
        p_lower = prompt.lower().strip()
        resolution = {"resolved_prompt": prompt, "entity": None, "reference_type": None}

        if not self.history:
            return resolution

        last_turn = self.history[-1]
        last_user = last_turn.get("user", "").lower()
        last_resp = last_turn.get("assistant", "")
        last_topic = last_turn.get("topic", self.active_topic)

        # 1. "it" resolution ("Why is it popular?", "What is it?")
        if " it" in p_lower or "it " in p_lower or p_lower.startswith("it "):
            if "python" in last_user or last_topic == "TECHNICAL":
                resolution["entity"] = "Python"
                resolution["reference_type"] = "PRONOUN_IT"
                events.log_emitted.emit("conversation", "Resolving reference: 'it' -> previous subject 'Python'")

        # 2. "that" resolution ("Is that bad?", "That was terrible", "That was weak", "What was that?")
        if "that" in p_lower:
            if "ram" in last_user or "cpu" in last_user or last_topic == "SYSTEM":
                resolution["entity"] = "RAM / System Telemetry"
                resolution["reference_type"] = "DEMONSTRATIVE_THAT_SYSTEM"
                events.log_emitted.emit("conversation", "Resolving reference: 'that' -> RAM usage telemetry")
            elif last_topic == "HUMOR" or any(w in last_user for w in ["joke", "roast"]):
                resolution["entity"] = last_resp
                resolution["reference_type"] = "DEMONSTRATIVE_THAT_HUMOR"
                events.log_emitted.emit("conversation", "Resolving reference: 'that' -> previous JARVIS joke/roast")

        # 3. Action repetition ("another one", "one more")
        if "another one" in p_lower or "one more" in p_lower:
            if last_topic == "HUMOR":
                resolution["entity"] = "HUMOR_REQUEST"
                resolution["reference_type"] = "ACTION_REPEAT_HUMOR"
                events.log_emitted.emit("conversation", "Resolving reference: 'another one' -> repeat joke request")

        return resolution

    def reset_memory(self):
        """Clears short-term conversational runtime memory."""
        self.history.clear()
        self.active_topic = "UNKNOWN"
        events.log_emitted.emit("conversation", "Memory reset requested")
        events.log_emitted.emit("conversation", "Conversation memory cleared")

    def get_history(self) -> List[Dict[str, str]]:
        """Returns simplified history for provider compatible formats."""
        res = []
        for t in self.history:
            res.append({"role": "user", "message": t["user"]})
            res.append({"role": "assistant", "message": t["assistant"]})
        return res
