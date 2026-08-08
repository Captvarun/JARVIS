from core.lifecycle import BaseLifecycleComponent
from core.brain.context import ContextManager
from core.brain.intent import IntentDetector
from core.brain.router import CommandRouter
from core.brain.provider import get_provider
from core.brain.response import StructuredResponse
from core.events import events
from core.logger import logger

class JarvisBrain(BaseLifecycleComponent):
    """
    Main JARVIS Intelligence Coordinator.
    Receives user input, maintains conversation context, runs intent detection,
    routes commands through safe handlers/providers, and emits events.
    """
    def __init__(self):
        super().__init__("JarvisBrain")
        self.context = ContextManager(max_turns=10)
        self.intent_detector = IntentDetector()
        self.router = CommandRouter()
        self.provider = None

    def on_initialize(self) -> bool:
        self.provider = get_provider()
        logger.info(f"[JarvisBrain] Initialized with provider: {self.provider.__class__.__name__}")
        return True

    def process_command(self, prompt: str) -> StructuredResponse:
        """
        Executes the command pipeline:
        User Input -> Intent Detection -> Router -> Provider/Tool -> Response -> History Update.
        """
        p_clean = prompt.strip()
        if not p_clean:
            return StructuredResponse(text="", success=False)

        try:
            logger.info(f"[JarvisBrain] Processing prompt: '{p_clean}'")

            # 1. Detect Intent
            intent_cat = self.intent_detector.detect(p_clean)
            events.log_emitted.emit("core", f"Intent detected: {intent_cat.value}")

            # 2. Get history context
            history = self.context.get_history()

            # 3. Route Command
            events.log_emitted.emit("core", "Routing request...")
            response = self.router.route(p_clean, intent_cat, self.provider, history)

            # 4. Save Context History
            self.context.add_turn("user", p_clean)
            self.context.add_turn("assistant", response.text)

            logger.info(f"[JarvisBrain] Execution successful | Action: {response.action}")
            return response

        except Exception as e:
            logger.error(f"[JarvisBrain] Error processing command: {e}")
            return StructuredResponse(
                text="An exception occurred while processing your request.",
                intent="error",
                success=False,
                action="ERROR_HANDLED"
            )

# Global Brain Singleton
brain = JarvisBrain()
