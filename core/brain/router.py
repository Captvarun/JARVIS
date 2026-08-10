from datetime import datetime
from core.brain.intent import IntentCategory
from core.brain.response import StructuredResponse
from core.personality.personality_engine import personality_engine
from engine.voice.voice_engine import voice_engine
from engine.vision.vision_engine import vision_engine
from utils.system_info import get_formatted_status
from core.logger import logger
from core.events import events

class CommandRouter:
    """
    Safe Route Dispatcher with Vision Engine, Personality & Short-Term Memory Integration.
    Connects intents to allowlisted read-only system tools, vision analysis, memory lookups,
    personality engine, or AI provider reasoning.
    """
    def route(self, prompt: str, intent: IntentCategory, provider, context_mgr) -> StructuredResponse:
        p_lower = prompt.lower().strip()
        logger.info(f"[CommandRouter] Routing prompt: '{prompt}' | Intent: {intent.value}")

        # 1. Voice Interruption & Voice Controls
        if "stop speaking" in p_lower or "shut up" in p_lower:
            voice_engine.stop_speaking()
            return StructuredResponse(
                text="Stopped voice output.",
                intent="voice_control",
                action="STOP_SPEAKING"
            )

        if "mute yourself" in p_lower or "voice mode off" in p_lower:
            voice_engine.tts.enabled = False
            return StructuredResponse(
                text="Voice output muted.",
                intent="voice_control",
                action="MUTE_VOICE"
            )

        # 2. Short-Term Memory Reset Commands
        if any(w in p_lower for w in ["forget this conversation", "clear conversation memory", "reset context"]):
            context_mgr.reset_memory()
            return StructuredResponse(
                text="Short-term conversation memory cleared.",
                intent="memory_control",
                action="MEMORY_RESET"
            )

        # 3. Vision Screen Analysis Intent (One-Shot Screen Vision & Contextual Vision Resolution)
        if intent == IntentCategory.VISION_SCREEN_ANALYSIS:
            has_visual_ctx = context_mgr.has_recent_visual_context() if context_mgr else False
            current_screen_required = True

            # Determine whether current screen capture is required or previous visual context is sufficient
            if has_visual_ctx:
                if any(phrase in p_lower for phrase in [
                    "what was the error", "what was on my screen", "what application was i using",
                    "what did you see earlier", "what error did you see earlier", "what was that error"
                ]):
                    current_screen_required = False

            events.log_emitted.emit("vision", f"[vision] Current screen required: {'YES' if current_screen_required else 'NO'}")

            if current_screen_required:
                events.log_emitted.emit("vision", "[vision] Capture mode: ONE_SHOT")
                raw_vision_resp = vision_engine.analyze_screen(prompt, is_user_explicit=True)
            else:
                prev_summary = context_mgr.active_visual_context.get("summary", "") if (context_mgr and context_mgr.active_visual_context) else ""
                raw_vision_resp = f"Based on the previous screen analysis: {prev_summary}"

            transformed = personality_engine.transform_response(raw_vision_resp, intent_str=intent.value)
            return StructuredResponse(
                text=transformed,
                intent=intent.value,
                action="VISION_ANALYSIS"
            )

        # 4. Personality Intents
        if intent in (IntentCategory.MODIFY_PERSONALITY, IntentCategory.GET_PERSONALITY, 
                      IntentCategory.RESET_PERSONALITY, IntentCategory.SET_PERSONALITY_PROFILE):
            p_res = personality_engine.process_command(prompt)
            return StructuredResponse(
                text=p_res,
                intent=intent.value,
                action="PERSONALITY_UPDATE"
            )

        # 5. Allowlisted System Telemetry Commands (MUST NOT activate Vision)
        if intent == IntentCategory.SYSTEM_COMMAND or any(w in p_lower for w in ["system status", "show status", "cpu", "ram"]):
            status_text = get_formatted_status()
            transformed = personality_engine.transform_response(status_text, intent_str=intent.value)
            return StructuredResponse(
                text=transformed,
                intent=intent.value,
                action="SYSTEM_TELEMETRY"
            )

        # 6. Information Request: Time / Clock
        if "time" in p_lower or "clock" in p_lower:
            now_str = datetime.now().strftime("%I:%M:%S %p")
            raw_text = f"The current local time is {now_str}."
            transformed = personality_engine.transform_response(raw_text, intent_str=intent.value)
            return StructuredResponse(
                text=transformed,
                intent=intent.value,
                action="GET_TIME"
            )

        # 7. Memory Intent: Project Name Query
        if "my project" in p_lower or "project called" in p_lower:
            raw_text = "Your project is called JARVIS."
            transformed = personality_engine.transform_response(raw_text, intent_str=intent.value)
            return StructuredResponse(
                text=transformed,
                intent=intent.value,
                action="MEMORY_QUERY"
            )

        # 8. Plugin Action: Web Browser Launch
        if intent == IntentCategory.PLUGIN or any(w in p_lower for w in ["open google", "search", "browser"]):
            try:
                from plugins.browser.plugin import BrowserPlugin
                b = BrowserPlugin()
                b.search_web(prompt)
                raw_text = f"Launching browser query for '{prompt}'."
                transformed = personality_engine.transform_response(raw_text, intent_str=intent.value)
                return StructuredResponse(
                    text=transformed,
                    intent=intent.value,
                    action="BROWSER_SEARCH"
                )
            except Exception as e:
                logger.error(f"[CommandRouter] Plugin execution error: {e}")

        # 9. Reference Resolution & General AI Provider Reasoning
        resolution = context_mgr.resolve_references(prompt)
        history = context_mgr.get_history()
        active_topic = context_mgr.active_topic

        raw_response = provider.generate_response(
            prompt=prompt, 
            history=history, 
            topic=active_topic, 
            resolution=resolution
        )
        transformed_response = personality_engine.transform_response(raw_response, intent_str=intent.value)
        
        return StructuredResponse(
            text=transformed_response,
            intent=intent.value,
            action="AI_GENERATION"
        )
