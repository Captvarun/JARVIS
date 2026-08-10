from datetime import datetime
from core.brain.intent import IntentCategory
from core.brain.response import StructuredResponse
from core.personality.personality_engine import personality_engine
from engine.voice.voice_engine import voice_engine
from utils.system_info import get_formatted_status
from core.logger import logger

class CommandRouter:
    """
    Safe Route Dispatcher with Personality Response Transformation.
    Connects intents to allowlisted read-only system tools, memory lookups,
    personality engine, or AI provider reasoning.
    """
    def route(self, prompt: str, intent: IntentCategory, provider, history: list) -> StructuredResponse:
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

        # 2. Personality Intents
        if intent in (IntentCategory.MODIFY_PERSONALITY, IntentCategory.GET_PERSONALITY, 
                      IntentCategory.RESET_PERSONALITY, IntentCategory.SET_PERSONALITY_PROFILE):
            p_res = personality_engine.process_command(prompt)
            return StructuredResponse(
                text=p_res,
                intent=intent.value,
                action="PERSONALITY_UPDATE"
            )

        # 3. Allowlisted System Telemetry Commands
        if intent == IntentCategory.SYSTEM_COMMAND or any(w in p_lower for w in ["system status", "show status", "cpu", "ram"]):
            status_text = get_formatted_status()
            transformed = personality_engine.transform_response(status_text)
            return StructuredResponse(
                text=transformed,
                intent=intent.value,
                action="SYSTEM_TELEMETRY"
            )

        # 4. Information Request: Time / Clock
        if "time" in p_lower or "clock" in p_lower:
            now_str = datetime.now().strftime("%I:%M:%S %p")
            raw_text = f"The current local time is {now_str}."
            transformed = personality_engine.transform_response(raw_text)
            return StructuredResponse(
                text=transformed,
                intent=intent.value,
                action="GET_TIME"
            )

        # 5. Memory Intent: Project Name Query
        if "my project" in p_lower or "project called" in p_lower:
            raw_text = "Your project is called JARVIS."
            transformed = personality_engine.transform_response(raw_text)
            return StructuredResponse(
                text=transformed,
                intent=intent.value,
                action="MEMORY_QUERY"
            )

        # 6. Plugin Action: Web Browser Launch
        if intent == IntentCategory.PLUGIN or any(w in p_lower for w in ["open google", "search", "browser"]):
            try:
                from plugins.browser.plugin import BrowserPlugin
                b = BrowserPlugin()
                b.search_web(prompt)
                raw_text = f"Launching browser query for '{prompt}'."
                transformed = personality_engine.transform_response(raw_text)
                return StructuredResponse(
                    text=transformed,
                    intent=intent.value,
                    action="BROWSER_SEARCH"
                )
            except Exception as e:
                logger.error(f"[CommandRouter] Plugin execution error: {e}")

        # 7. General AI Provider Reasoning
        raw_response = provider.generate_response(prompt, history)
        transformed_response = personality_engine.transform_response(raw_response)
        return StructuredResponse(
            text=transformed_response,
            intent=intent.value,
            action="AI_GENERATION"
        )
