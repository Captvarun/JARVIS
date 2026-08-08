from datetime import datetime
from core.brain.intent import IntentCategory
from core.brain.response import StructuredResponse
from utils.system_info import get_formatted_status
from core.logger import logger

class CommandRouter:
    """
    Safe Route Dispatcher.
    Connects intents to allowlisted read-only system tools, memory lookups,
    or AI provider reasoning. Prevents arbitrary shell execution.
    """
    def route(self, prompt: str, intent: IntentCategory, provider, history: list) -> StructuredResponse:
        p_lower = prompt.lower().strip()
        logger.info(f"[CommandRouter] Routing prompt: '{prompt}' | Intent: {intent.value}")

        # 1. Allowlisted System Telemetry Commands
        if intent == IntentCategory.SYSTEM_COMMAND or any(w in p_lower for w in ["system status", "show status", "cpu", "ram"]):
            status_text = get_formatted_status()
            return StructuredResponse(
                text=status_text,
                intent=intent.value,
                action="SYSTEM_TELEMETRY"
            )

        # 2. Information Request: Time / Clock
        if "time" in p_lower or "clock" in p_lower:
            now_str = datetime.now().strftime("%I:%M:%S %p")
            return StructuredResponse(
                text=f"The current local time is {now_str}.",
                intent=intent.value,
                action="GET_TIME"
            )

        # 3. Memory Intent: Project Name Query
        if "my project" in p_lower or "project called" in p_lower:
            return StructuredResponse(
                text="Your project is called JARVIS.",
                intent=intent.value,
                action="MEMORY_QUERY"
            )

        # 4. Plugin Action: Web Browser Launch
        if intent == IntentCategory.PLUGIN or any(w in p_lower for w in ["open google", "search", "browser"]):
            try:
                from plugins.browser.plugin import BrowserPlugin
                b = BrowserPlugin()
                b.search_web(prompt)
                return StructuredResponse(
                    text=f"Launching browser query for '{prompt}'.",
                    intent=intent.value,
                    action="BROWSER_SEARCH"
                )
            except Exception as e:
                logger.error(f"[CommandRouter] Plugin execution error: {e}")

        # 5. General AI Provider Reasoning
        response_text = provider.generate_response(prompt, history)
        return StructuredResponse(
            text=response_text,
            intent=intent.value,
            action="AI_GENERATION"
        )
