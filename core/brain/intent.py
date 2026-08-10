from enum import Enum
from core.logger import logger
from core.events import events

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
    VISION_SCREEN_ANALYSIS = "vision_screen_analysis"
    UNKNOWN = "unknown"

class IntentDetector:
    """
    Analyzes natural-language input to classify intent.
    Implements Milestone 6 Patch 2: High-Confidence Implicit Vision Intent Detection.
    Resolves queries like 'What am I seeing?' to VISION_SCREEN_ANALYSIS without prior context,
    while accurately avoiding conversational false-positives ('Do you see what I mean?').
    """
    def detect(self, prompt: str, context_mgr=None) -> IntentCategory:
        p = prompt.lower().strip()

        if not p:
            return IntentCategory.UNKNOWN

        has_visual_ctx = False
        if context_mgr and hasattr(context_mgr, "has_recent_visual_context"):
            has_visual_ctx = context_mgr.has_recent_visual_context()

        # 0. Conversational Idioms Exclusion (Prevent false-positives on conversational speech)
        conversational_idioms = [
            "do you see what i mean", "do you see my point", "do you see how",
            "what do you think", "in this situation", "what's wrong with my life",
            "tell me a joke", "how are you"
        ]
        if any(idiom in p for idiom in conversational_idioms) and not ("screen" in p or "code" in p or "error" in p):
            return IntentCategory.CONVERSATION

        # 1. High-Confidence Visual Questions (Work WITH or WITHOUT previous visual context)
        high_confidence_visual_questions = [
            "what am i seeing", "what am i looking at", "what do you see on my screen",
            "what do you see", "what can you see", "describe what you see", "describe my screen",
            "what's on my screen", "what is on my screen", "can you see my screen",
            "can you see my code", "can you read this", "what does this say",
            "what's wrong with this", "do you see any errors", "do you see an error",
            "what error do you see", "where is the problem", "what is happening on my screen",
            "analyze my screen", "look at my screen", "inspect my screen", "scan my screen",
            "describe the important things you can see on my screen", "screen analysis"
        ]

        if any(w in p for w in high_confidence_visual_questions):
            logger.info("[core] Intent candidate: VISION_SCREEN_ANALYSIS")
            events.log_emitted.emit("core", "[core] Intent candidate: VISION_SCREEN_ANALYSIS")
            if has_visual_ctx:
                logger.info("[conversation] Recent visual context: AVAILABLE")
                events.log_emitted.emit("conversation", "[conversation] Recent visual context: AVAILABLE")
            else:
                logger.info("[conversation] Recent visual context: NONE")
                events.log_emitted.emit("conversation", "[conversation] Recent visual context: NONE")
                logger.info("[vision] Visual question confidence: HIGH")
                events.log_emitted.emit("vision", "[vision] Visual question confidence: HIGH")

            logger.info("[core] Final intent: VISION_SCREEN_ANALYSIS")
            events.log_emitted.emit("core", "[core] Final intent: VISION_SCREEN_ANALYSIS")
            return IntentCategory.VISION_SCREEN_ANALYSIS

        # 2. Contextual / Implicit Vision Follow-up Triggers (Require active recent visual context)
        implicit_vision_followups = [
            "what else am i doing", "what was the error", "what was the error you saw",
            "what was the thing you saw earlier", "what did you see earlier",
            "did it disappear", "did the error disappear", "is the error still there",
            "did anything change", "what's on my screen right now", "what's on my screen now",
            "what should i do next"
        ]

        if has_visual_ctx:
            matched_phrase = next((w for w in implicit_vision_followups if w in p), None)
            matched_ref = None
            if not matched_phrase and any(ref in p for ref in ["this", "that", "it", "here", "there"]):
                if any(kw in p for kw in ["see", "code", "error", "doing", "screen", "problem", "disappear", "change", "look"]):
                    matched_ref = next((ref for ref in ["this", "that", "it", "here", "there"] if ref in p), "visual reference")

            if matched_phrase or matched_ref:
                logger.info("[core] Intent candidate: VISION_SCREEN_ANALYSIS")
                events.log_emitted.emit("core", "[core] Intent candidate: VISION_SCREEN_ANALYSIS")
                logger.info("[conversation] Recent visual context: AVAILABLE")
                events.log_emitted.emit("conversation", "[conversation] Recent visual context: AVAILABLE")
                logger.info("[core] Final intent: VISION_SCREEN_ANALYSIS")
                events.log_emitted.emit("core", "[core] Final intent: VISION_SCREEN_ANALYSIS")
                return IntentCategory.VISION_SCREEN_ANALYSIS
        else:
            if any(w in p for w in implicit_vision_followups):
                logger.info("[conversation] Recent visual context: NONE")
                events.log_emitted.emit("conversation", "[conversation] Recent visual context: NONE")

        # 3. High-Priority Personality Queries
        if any(w in p for w in [
            "what's your personality", "what is your personality", "show your personality",
            "current settings", "current personality", "sarcasm level", "humor level",
            "empathy level", "formality level", "energy level", "verbosity level",
            "confidence level", "friendliness level", "how sarcastic are you",
            "how humorous are you", "how formal are you", "personality parameters",
            "personality settings"
        ]):
            return IntentCategory.GET_PERSONALITY

        # 4. Personality Reset
        if ("reset" in p and "personality" in p) or "default personality" in p:
            return IntentCategory.RESET_PERSONALITY

        # 5. Profile Switch
        if any(w in p for w in ["professional mode", "companion mode", "sarcastic mode", "focus mode", "switch to", "profile", "go into"]):
            return IntentCategory.SET_PERSONALITY_PROFILE

        # 6. Personality Parameter Modification & Tuning Commands
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

        # 7. System Command Intent (Telemetries MUST NOT trigger Vision)
        if any(w in p for w in ["system status", "cpu", "ram", "disk", "uptime", "os", "specs", "telemetry"]):
            return IntentCategory.SYSTEM_COMMAND

        # 8. Information Request Intent
        if any(w in p for w in ["what time", "current time", "date", "clock", "what is my name", "what can you do"]):
            return IntentCategory.INFORMATION_REQUEST

        # 9. Memory Query Intent
        if any(w in p for w in ["my project", "what is my project", "remember", "recall"]):
            return IntentCategory.MEMORY

        # 10. Plugin Intent
        if any(w in p for w in ["browser", "open google", "search", "youtube", "github", "spotify", "weather"]):
            return IntentCategory.PLUGIN

        # 11. General Conversation Intent
        return IntentCategory.CONVERSATION
