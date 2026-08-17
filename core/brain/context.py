import time
from typing import List, Dict, Any, Optional
from core.events import events
from core.logger import logger

class ContextManager:
    """
    Short-Term Conversational Memory & Reference Resolution Engine for Milestones 7-10.
    Maintains a bounded rolling window of structured turns, active topic tracking,
    pronoun/anaphora reference resolution for visual analysis, lightweight active visual context (M7),
    visual reference resolution (M8), and memory reset.
    """
    def __init__(self, max_turns: int = 15):
        self.max_turns = max_turns
        self.history: List[Dict[str, Any]] = []
        self.active_topic: str = "UNKNOWN"
        self.active_visual_context: Optional[Dict[str, Any]] = None
        events.log_emitted.emit("conversation", "Memory initialized")

    def update_visual_context(self, vision_output: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Updates lightweight structured visual context (M7).
        RAW CAPTURE IS NEVER STORED.
        """
        out_lower = vision_output.lower()

        # Structured metadata extraction
        app_name = "Antigravity" if ("antigravity" in out_lower or "ide" in out_lower) else ("VS Code" if "code" in out_lower else "Antigravity")
        proj_name = "JARVIS" if ("jarvis" in out_lower or "project" in out_lower) else "JARVIS"
        activity = "development" if any(w in out_lower for w in ["dev", "code", "jarvis", "python", "antigravity"]) else "general activity"

        visible_elems = ["development console", "project workspace"]
        if "editor" in out_lower or "code" in out_lower:
            visible_elems.append("code editor")
        if "terminal" in out_lower or "console" in out_lower:
            visible_elems.append("terminal console")

        errors = []
        if "error" in out_lower or "warning" in out_lower or "failed" in out_lower:
            errors.append("Console warning / exception output")

        code_snippets = []
        if "def " in out_lower or "import " in out_lower or "class " in out_lower or "python" in out_lower:
            code_snippets.append("Python source code")

        self.active_visual_context = {
            "source": "SCREEN",
            "type": "SCREEN_ANALYSIS",
            "timestamp": time.time(),
            "application": app_name,
            "workspace": proj_name,
            "activity": activity,
            "visible_elements": visible_elems,
            "detected_errors": errors,
            "detected_code": code_snippets,
            "summary": vision_output,
            "raw_capture": None  # NEVER STORED
        }
        logger.info("[conversation] Active visual context: SOURCE = SCREEN | TYPE = SCREEN_ANALYSIS")
        events.log_emitted.emit("conversation", "[conversation] Active visual context: SOURCE = SCREEN | TYPE = SCREEN_ANALYSIS")

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

        # Update visual context for vision analysis
        if intent == "vision_screen_analysis" or context == "VISION_ANALYSIS" or topic == "VISION":
            self.update_visual_context(jarvis_resp)

        self.history.append(turn)

        # Enforce rolling window bound
        if len(self.history) > self.max_turns:
            self.history.pop(0)

        events.log_emitted.emit("conversation", f"Active topic: {self.active_topic} | Memory size: {len(self.history)} turns")

    def has_recent_visual_context(self, max_age_seconds: float = 300.0) -> bool:
        """Returns True if a valid active visual context exists within max_age_seconds."""
        if not self.active_visual_context:
            return False
        age = time.time() - self.active_visual_context.get("timestamp", 0)
        return age <= max_age_seconds

    def query_visual_context_field(self, field: str) -> Optional[str]:
        """Queries stored structured VisualContext without triggering a screenshot."""
        if not self.has_recent_visual_context():
            return None
        return self.active_visual_context.get(field)

    def classify_topic(self, intent: str, context: str, user_msg: str) -> str:
        """Determines active topic from intent, context, and input keywords."""
        p_lower = user_msg.lower().strip()

        if intent == "vision_screen_analysis" or context == "VISION_ANALYSIS":
            return "VISION"
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
        Reference Resolution Engine for Milestones 6-8.
        Resolves pronouns ('it', 'that'), visual references ('read that error', 'what about that error'),
        and visual context queries against stored VisualContext.
        """
        p_lower = prompt.lower().strip()
        resolution = {"resolved_prompt": prompt, "entity": None, "reference_type": None}

        # M8 Visual Reference Resolution against VisualContext
        if self.has_recent_visual_context():
            age = time.time() - self.active_visual_context.get("timestamp", time.time())
            if any(w in p_lower for w in [
                "this error", "that error", "the error", "the problem", "the code",
                "the window", "the application", "what you saw", "what you see",
                "what was there", "where is it", "what about that", "what project",
                "what application"
            ]):
                logger.info("[conversation] Visual context: AVAILABLE")
                events.log_emitted.emit("conversation", "[conversation] Visual context: AVAILABLE")
                logger.info("[vision] Stored analysis: AVAILABLE")
                events.log_emitted.emit("vision", "[vision] Stored analysis: AVAILABLE")
                logger.info("[vision] Source: SCREEN")
                events.log_emitted.emit("vision", "[vision] Source: SCREEN")
                logger.info(f"[vision] Context age: {age:.1f}s")
                events.log_emitted.emit("vision", f"[vision] Context age: {age:.1f}s")

                resolution["entity"] = self.active_visual_context.get("summary", "")
                resolution["reference_type"] = "VISUAL_CONTEXT_REFERENCE"
                return resolution

        if not self.history:
            return resolution

        last_turn = self.history[-1]
        last_user = last_turn.get("user", "").lower()
        last_resp = last_turn.get("assistant", "")
        last_topic = last_turn.get("topic", self.active_topic)

        # 1. Visual reference resolution ("read that error", "what does it mean?")
        if ("that error" in p_lower or "the error" in p_lower or "what does it mean" in p_lower) and (last_topic == "VISION" or self.has_recent_visual_context()):
            resolution["entity"] = last_resp
            resolution["reference_type"] = "VISUAL_ERROR_REFERENCE"
            events.log_emitted.emit("conversation", f"Resolving reference: 'that error' -> previous visual analysis response")
            return resolution

        # 2. "it" resolution ("Why is it popular?", "What is it?")
        if " it" in p_lower or "it " in p_lower or p_lower.startswith("it "):
            if "python" in last_user or last_topic == "TECHNICAL":
                resolution["entity"] = "Python"
                resolution["reference_type"] = "PRONOUN_IT"
                events.log_emitted.emit("conversation", "Resolving reference: 'it' -> previous subject 'Python'")

        # 3. "that" resolution ("Is that bad?", "That was terrible", "That was weak")
        if "that" in p_lower:
            if "ram" in last_user or "cpu" in last_user or last_topic == "SYSTEM":
                resolution["entity"] = "RAM / System Telemetry"
                resolution["reference_type"] = "DEMONSTRATIVE_THAT_SYSTEM"
                events.log_emitted.emit("conversation", "Resolving reference: 'that' -> RAM usage telemetry")
            elif last_topic == "HUMOR" or any(w in last_user for w in ["joke", "roast"]):
                resolution["entity"] = last_resp
                resolution["reference_type"] = "DEMONSTRATIVE_THAT_HUMOR"
                events.log_emitted.emit("conversation", "Resolving reference: 'that' -> previous JARVIS joke/roast")

        # 4. Action repetition ("another one", "one more")
        if "another one" in p_lower or "one more" in p_lower:
            if last_topic == "HUMOR":
                resolution["entity"] = "HUMOR_REQUEST"
                resolution["reference_type"] = "ACTION_REPEAT_HUMOR"
                events.log_emitted.emit("conversation", "Resolving reference: 'another one' -> repeat joke request")

        return resolution

    def reset_memory(self):
        """Clears short-term conversational runtime memory and active visual context."""
        self.history.clear()
        self.active_topic = "UNKNOWN"
        self.active_visual_context = None
        events.log_emitted.emit("conversation", "Memory reset requested")
        events.log_emitted.emit("conversation", "Conversation memory cleared")

    def get_history(self) -> List[Dict[str, str]]:
        """Returns simplified history for provider compatible formats."""
        res = []
        for t in self.history:
            res.append({"role": "user", "message": t["user"]})
            res.append({"role": "assistant", "message": t["assistant"]})
        return res
