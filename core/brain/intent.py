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
    Implements Milestones 6-10: Vision Intelligence Upgrade & Non-Vision Protection.
    Supports compound visual requests (Observation + Diagnosis + Recommendation).
    Disambiguates explicit codebase inspection requests from desktop screen vision analysis.
    """
    def detect(self, prompt: str, context_mgr=None) -> IntentCategory:
        p = prompt.lower().strip()

        if not p:
            return IntentCategory.UNKNOWN

        has_visual_ctx = False
        if context_mgr and hasattr(context_mgr, "has_recent_visual_context"):
            has_visual_ctx = context_mgr.has_recent_visual_context()

        # 0. Non-Vision Conversational Idioms Exclusion (Strict Protection)
        conversational_idioms = [
            "do you see what i mean", "do you see my point", "do you see how",
            "what do you think", "in this situation", "what's wrong with my life",
            "tell me a joke", "how are you", "is it funny", "how is it going",
            "tell me a story", "good morning", "i'm bored", "im bored"
        ]
        if any(idiom in p for idiom in conversational_idioms) and not any(kw in p for kw in ["screen", "code", "error", "window"]):
            return IntentCategory.CONVERSATION

        # 0.1 Explicit Codebase / Source Code Inspection Exclusion (Prevent screen vision hijacking)
        codebase_inspection_phrases = [
            "inspect project files", "inspect source code", "inspect the intent detector",
            "inspect code", "debug source code", "debug your code", "read core/", "read engine/",
            "read tests/", "inspect the vision pipeline", "inspect python files", "code architecture",
            "jarvis project source code", "jarvis project files"
        ]
        if any(phrase in p for phrase in codebase_inspection_phrases) or (
            any(w in p for w in ["source code", "codebase", "repository", "py file", ".py"]) and not any(v in p for v in ["screen", "window", "monitor", "display"])
        ):
            return IntentCategory.CONVERSATION

        # 1. High-Confidence Visual Questions (Work WITH or WITHOUT previous visual context)
        high_confidence_visual_questions = [
            "what am i seeing", "what am i looking at", "what do you see on my screen",
            "what do you see", "what can you see", "describe what you see", "describe my screen",
            "what's on my screen", "what is on my screen", "can you see my screen",
            "can you see my code", "can you read this", "what does this say",
            "what's wrong with this", "do you see any errors", "do you see an error",
            "what error do you see", "where is the problem", "what is happening on my screen",
            "analyze my screen", "analyse my screen", "look at my screen", "inspect my screen", "scan my screen",
            "describe the important things you can see on my screen", "screen analysis",
            "what did you just see", "what do you see and what should i do",
            "what's wrong here and how do i fix it", "what did you notice and what's my next step",
            "based on what you see", "what's wrong with what you're seeing", "what's the next step"
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
            "what application am i using", "what app am i using", "what application was i using",
            "what project am i working on", "what project was i working on",
            "what else am i doing", "what was the error", "what was the error you saw",
            "what was the thing you saw earlier", "what did you see earlier", "what did you see previously",
            "what was that error", "what did you notice", "where was the problem",
            "do you see any errors", "is it still there", "is it still visible", "is that still there",
            "is the error still there", "did it disappear", "did the error disappear", "is it gone",
            "has it changed", "did anything change", "what's different now", "is the problem still there",
            "can you still see it", "do you still see that", "is that fixed", "did the error get fixed",
            "does it still show", "is it showing now", "is the application still open",
            "what's on my screen right now", "what's on my screen now", "what should i do next",
            "what about that error", "what about that", "how do i fix it", "next step", "what to fix first"
        ]

        if has_visual_ctx:
            matched_phrase = next((w for w in implicit_vision_followups if w in p), None)
            matched_ref = None
            if not matched_phrase and any(ref in p for ref in ["this", "that", "it", "here", "there", "error", "warning", "problem", "code", "button", "window", "project", "app", "application"]):
                if any(kw in p for kw in ["see", "code", "error", "doing", "screen", "problem", "disappear", "change", "look", "still", "gone", "fixed", "show", "open", "working", "using", "next"]):
                    matched_ref = next((ref for ref in ["this", "that", "it", "here", "there", "error"] if ref in p), "visual reference")

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
