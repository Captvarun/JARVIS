from typing import Optional, Any
from engine.vision.screen_capture import ScreenCapture
from engine.vision.provider import get_vision_provider, BaseVisionProvider
from core.events import events
from core.logger import logger

class VisionEngine:
    """
    JARVIS Vision Subsystem Coordinator.
    Implements Privacy-First One-Shot Screen Vision without continuous polling.
    """
    def __init__(self):
        self.provider: BaseVisionProvider = get_vision_provider()
        self.camera_active: bool = False
        events.log_emitted.emit("vision", "Vision Engine Subsystem initialized (Privacy Check: ONE_SHOT ONLY)")

    def analyze_screen(self, prompt: str, is_user_explicit: bool = True) -> str:
        """
        Executes Privacy-First One-Shot Screen Analysis:
        Privacy Check -> Capture Screen Once -> Vision Provider Analysis -> Discard Capture.
        """
        if not is_user_explicit:
            logger.warning("[vision] Aborted: Automatic background screenshot attempt blocked by Privacy Engine.")
            events.log_emitted.emit("vision", "[vision] Privacy check: FAILED (Background capture blocked)")
            return "Vision analysis activates only after an explicit user request."

        events.log_emitted.emit("vision", "[vision] Source: SCREEN")
        events.log_emitted.emit("vision", "[vision] Capture mode: ONE_SHOT")
        events.log_emitted.emit("vision", "[vision] Privacy check: PASSED")
        events.vision_state_changed.emit("ANALYZING")

        image: Any = None
        try:
            # 1. One-Shot Screen Capture
            image = ScreenCapture.capture_oneshot()
            if not image:
                events.log_emitted.emit("vision", "[vision] Capture failed | Reason: Screen capture returned null")
                return "I was unable to capture the screen."

            # 2. Vision Provider Analysis
            prov_name = self.provider.__class__.__name__
            logger.info(f"[vision] Vision provider: {prov_name}")
            events.log_emitted.emit("vision", f"[vision] Vision provider: {prov_name}")
            events.log_emitted.emit("vision", "[vision] Analysis started")

            analysis_result = self.provider.analyze_image(image, prompt)

            events.log_emitted.emit("vision", "[vision] Analysis completed")
            return analysis_result

        except Exception as e:
            logger.error(f"[vision] Vision analysis error: {e}")
            events.log_emitted.emit("vision", f"[vision] Analysis error: {e}")
            return "An error occurred while analyzing the screen."
        finally:
            # 3. Discard temporary capture immediately from memory
            if image and hasattr(image, "close"):
                try:
                    image.close()
                except Exception:
                    pass
            image = None
            logger.info("[vision] Temporary capture discarded")
            events.log_emitted.emit("vision", "[vision] Temporary capture discarded")
            events.vision_state_changed.emit("STANDBY")

# Global VisionEngine Singleton
vision_engine = VisionEngine()
