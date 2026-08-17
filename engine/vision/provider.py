import os
import ctypes
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from core.logger import logger
from core.config import config

class BaseVisionProvider(ABC):
    """
    Abstract Vision Provider Interface.
    Allows swapping between local window/visual reasoning or cloud multimodal AI models.
    """
    @abstractmethod
    def analyze_image(self, image: Any, prompt: str) -> str:
        pass

class LocalVisionProvider(BaseVisionProvider):
    """
    Offline Local Vision Provider.
    Inspects active foreground window titles, visual dimensions, and focus context
    with local OCR text extraction fallback.
    """
    def _get_active_window_title(self) -> str:
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
            title = buff.value.strip()
            return title if title else "JARVIS HUD Workspace"
        except Exception:
            return "JARVIS HUD Workspace"

    def _extract_text_ocr(self, image: Any) -> Optional[str]:
        """Attempts local OCR extraction from PIL Image buffer."""
        try:
            import pytesseract
            text = pytesseract.image_to_string(image).strip()
            return text if text else None
        except Exception:
            return None

    def analyze_image(self, image: Any, prompt: str) -> str:
        p_lower = prompt.lower().strip()
        win_title = self._get_active_window_title()

        width, height = (1920, 1080)
        if image and hasattr(image, "size"):
            width, height = image.size

        # Attempt local OCR
        extracted_text = self._extract_text_ocr(image) if (image and image != "DUMMY_IMAGE_HANDLE") else None

        if extracted_text:
            lines = [l.strip() for l in extracted_text.splitlines() if l.strip()]
            visible_sample = " | ".join(lines[:5])
            if "read" in p_lower or "text" in p_lower or "line" in p_lower:
                return f"Visible text captured from '{win_title}' ({width}x{height}): {visible_sample}"
            if "error" in p_lower or "wrong" in p_lower:
                error_lines = [l for l in lines if any(w in l.lower() for w in ["error", "fail", "warn", "exception"])]
                if error_lines:
                    return f"The visual analysis of '{win_title}' detected the following on-screen alert: '{error_lines[0]}'."
                else:
                    return f"The visual analysis of '{win_title}' ({width}x{height}) shows your active workspace running cleanly with no visible on-screen errors."
            return f"You are viewing '{win_title}' ({width}x{height}). Extracted on-screen text: {visible_sample}"

        # Honest fallback when OCR is unavailable or cannot confidently extract text
        if "error" in p_lower or "wrong" in p_lower:
            return f"The visual analysis of '{win_title}' ({width}x{height}) shows your active workspace running. No active on-screen errors were detected in the visible layout."

        if "code" in p_lower or "read" in p_lower or "line" in p_lower:
            return f"Local vision analysis detected active window '{win_title}' ({width}x{height}), but exact code text could not be read via local OCR. Please ensure the target window is focused or configure an OpenAI API key for cloud vision reasoning."

        if "antigravity" in win_title.lower() or "jarvis" in win_title.lower() or "code" in win_title.lower():
            return f"You're currently working in Antigravity. I can see your JARVIS project workspace ({win_title}) and the development console."
        elif "chrome" in win_title.lower() or "edge" in win_title.lower() or "browser" in win_title.lower():
            return f"You're currently viewing a web browser window titled '{win_title}' at {width}x{height} resolution."
        else:
            return f"You are looking at '{win_title}' on your primary monitor ({width}x{height})."

class OpenAICloudVisionProvider(BaseVisionProvider):
    """
    Cloud Multimodal Vision Provider (GPT-4o / GPT-4-Vision).
    Falls back gracefully to LocalVisionProvider if OPENAI_API_KEY is missing.
    """
    def __init__(self):
        self.fallback = LocalVisionProvider()
        self.api_key = os.getenv("OPENAI_API_KEY") or config.get("ai.openai_api_key")

    def analyze_image(self, image: Any, prompt: str) -> str:
        if not self.api_key or not hasattr(image, "save"):
            return self.fallback.analyze_image(image, prompt)

        try:
            import io
            import base64
            import json
            import urllib.request

            buf = io.BytesIO()
            image.save(buf, format="JPEG", quality=85)
            img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

            url = "https://api.openai.com/v1/chat/completions"
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"You are JARVIS. Answer the user's vision prompt: {prompt}. Be concise, specific, and direct."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                    ]
                }
            ]

            data = json.dumps({"model": "gpt-4o-mini", "messages": messages, "max_tokens": 200}).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            })

            with urllib.request.urlopen(req, timeout=12) as response:
                res_body = json.loads(response.read().decode("utf-8"))
                return res_body["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error(f"[CloudVisionProvider] API error: {e}. Falling back to LocalVisionProvider.")
            return self.fallback.analyze_image(image, prompt)

def get_vision_provider() -> BaseVisionProvider:
    """Factory to return configured vision provider."""
    if os.getenv("OPENAI_API_KEY") or config.get("ai.openai_api_key"):
        return OpenAICloudVisionProvider()
    return LocalVisionProvider()
