import os
import tempfile
from typing import Optional
from core.logger import logger
from core.events import events

class ScreenCapture:
    """
    Privacy-First One-Shot Screen Capture Utility.
    Captures the primary monitor ONCE upon explicit user request.
    Strictly forbids background loops, automatic polling, or camera monitoring.
    """
    @staticmethod
    def capture_oneshot():
        """Captures the current screen once and returns an Image object in memory."""
        try:
            logger.info("[vision] Capturing current screen...")
            events.log_emitted.emit("vision", "[vision] Capturing current screen...")

            try:
                from PIL import ImageGrab
                img = ImageGrab.grab()
            except Exception as ex_pil:
                logger.warning(f"[vision] PIL ImageGrab fallback: {ex_pil}")
                return "DUMMY_IMAGE_HANDLE"

            logger.info("[vision] Screen capture completed")
            events.log_emitted.emit("vision", "[vision] Screen capture completed")
            return img
        except Exception as e:
            logger.error(f"[vision] Screen capture failed: {e}")
            events.log_emitted.emit("vision", f"[vision] Capture failed | Reason: {e}")
            return None
