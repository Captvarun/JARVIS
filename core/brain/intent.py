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
    Implements Milestone 6 Patch: Contextual Vision Intent Detection.
    Combines user prompt, recent conversation context, and active visual context.
    """
    def detect(self, prompt: str, context_mgr=None) -> IntentCategory:
        p = prompt.lower().strip()

        if not p:
            return IntentCategory.UNKNOWN

        has_visual_ctx = False
        if context_mgr and hasattr(context_mgr, "has_recent_visual_context"):
            has_visual_ctx = context_mgr.has_recent_visual_context()

        # 1. Explicit Screen Vision Phrases (ALWAYS trigger VISION_SCREEN_ANALYSIS)
        explicit_vision_phrases = [
            "analyze my screen", "look at my screen", "what am i looking at",
            "what's on my screen", "what is on my screen", "read my screen",
            "inspect my screen", "scan my screen", "describe the important things you can see on my screen",
            "can you see my code", "describe what you see", "what else can you see",
            "screen analysis"
        ]

        if any(w in p for w in explicit_vision_phrases):
            logger.info("[core] Intent candidate: VISION_SCREEN_ANALYSIS")
            events.log_emitted.emit("core", "[core] Intent candidate: VISION_SCREEN_ANALYSIS")
            if has_visual_ctx:
                events.log_emitted.emit("conversation", "[conversation] Recent visual context: AVAILABLE")
            else:
                events.log_emitted.emit("conversation", "[conversation] Recent visual context: NOT_AVAILABLE")
            logger.info("[core] Final intent: VISION_SCREEN_ANALYSIS")
            events.log_emitted.emit("core", "[core] Final intent: VISION_SCREEN_ANALYSIS")
            return IntentCategory.VISION_SCREEN_ANALYSIS

        # 2. Contextual / Implicit Vision Triggers (Require recent visual context or specific visual keywords)
        implicit_vision_phrases = [
            "what else am i doing", "what do you see", "what error is that",
            "what error do you see", "what was the error", "what does that say",
            "where is the problem", "what's wrong with this", "what should i do next",
            "did it disappear", "did anything change", "what's on my screen now"
        ]
        visual_ref_tokens = ["this", "that", "it", "here", "there"]

        if has_visual_ctx:
            matched_phrase = next((w for w in implicit_vision_phrases if w in p), None)
            matched_ref = None
            if not matched_phrase and any(ref in p for ref in visual_ref_tokens):
                if any(kw in p for kw in ["see", "code", "error", "doing", "screen", "problem", "disappear", "change", "look"]):
                    matched_ref = next((ref for ref in visual_ref_tokens if ref in p), "visual reference")

            if matched_phrase or matched_ref:
                ref_text = matched_phrase or matched_ref
                logger.info("[core] Intent candidate: VISION_SCREEN_ANALYSIS")
                events.log_emitted.emit("core", "[core] Intent candidate: VISION_SCREEN_ANALYSIS")
                events.log_emitted.emit("conversation", "[conversation] Recent visual context: AVAILABLE")
                logger.info(f'[conversation] Visual reference detected: "{ref_text}"')
                events.log_emitted.emit("conversation", f'[conversation] Visual reference detected: "{ref_text}"')
                logger.info("[core] Final intent: VISION_SCREEN_ANALYSIS")
                events.log_emitted.emit("core", "[core] Final intent: VISION_SCREEN_ANALYSIS")
                return IntentCategory.VISION_SCREEN_ANALYSIS
        else:
            if any(w in p for w in implicit_vision_phrases):
                events.log_emitted.emit("conversation", "[conversation] Recent visual context: NOT_AVAILABLE")

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
