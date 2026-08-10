from core.lifecycle import BaseLifecycleComponent
from core.brain.context import ContextManager
from core.brain.intent import IntentDetector
from core.brain.router import CommandRouter
from core.brain.provider import get_provider
from core.brain.response import StructuredResponse
from core.personality.personality_engine import personality_engine
from core.events import events
from core.logger import logger

class JarvisBrain(BaseLifecycleComponent):
    """
    Main JARVIS Intelligence Coordinator.
    Receives user input, maintains short-term conversation memory, runs intent detection,
    routes commands through safe handlers/providers, and emits events.
    """
    def __init__(self):
        super().__init__("JarvisBrain")
        self.context = ContextManager(max_turns=15)
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
        User Input -> Intent Detection -> Router -> Provider/Tool -> Short-term Memory Update.
        """
        p_clean = prompt.strip()
        if not p_clean:
            return StructuredResponse(text="", success=False)

        try:
            logger.info(f"[JarvisBrain] Processing prompt: '{p_clean}'")

            # 1. Detect Intent
            intent_cat = self.intent_detector.detect(p_clean)
            events.log_emitted.emit("core", f"Intent detected: {intent_cat.value}")

            # 2. Route Command & Resolve References
            events.log_emitted.emit("core", "Routing request...")
            response = self.router.route(p_clean, intent_cat, self.provider, self.context)

            # 3. Save Structured Turn in Short-Term Memory (unless Memory Reset)
            if response.action != "MEMORY_RESET":
                context_tag = personality_engine.context_mgr.context_tag
                resp_mode = personality_engine.context_mgr.determine_response_mode(
                    context_tag, 
                    personality_engine.context_mgr.evaluate_humor_decision(context_tag, personality_engine.state.get("humor"), 5),
                    personality_engine.context_mgr.evaluate_sarcasm_decision(context_tag, personality_engine.state.get("sarcasm"), 5)
                )

                self.context.add_turn(
                    user_msg=p_clean,
                    jarvis_resp=response.text,
                    intent=intent_cat.value,
                    context=context_tag,
                    response_mode=resp_mode
                )

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
