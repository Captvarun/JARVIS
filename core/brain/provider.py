import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from core.logger import logger
from core.config import config

class BaseAIProvider(ABC):
    """
    Abstract AI Provider Interface.
    Allows swapping between OpenAI API, local LLMs (Ollama), or local offline rules.
    """
    @abstractmethod
    def generate_response(self, prompt: str, history: List[Dict[str, str]]) -> str:
        pass

class LocalMockProvider(BaseAIProvider):
    """
    Offline Local Intelligence Provider.
    Implements rule and context template reasoning without requiring an external API key.
    """
    def __init__(self):
        self.operator_name = config.get("system.operator", "Varun")

    def generate_response(self, prompt: str, history: List[Dict[str, str]]) -> str:
        p_lower = prompt.lower().strip()

        # Personality & Identity
        if "who are you" in p_lower or "what are you" in p_lower:
            return f"I am JARVIS, your personal AI interface. My core handles reasoning and conversation, while connected subsystems manage voice, vision, system telemetry, and plugins."

        if "what can you do" in p_lower or "capabilities" in p_lower or "help" in p_lower:
            return ("Here are my currently active capabilities:\n"
                    "• System Telemetry: Check CPU, RAM, Disk, Uptime, and OS details ('show system status')\n"
                    "• Time & Date: Precision clock queries ('what time is it')\n"
                    "• Browser Plugin: Launch web queries ('open google', 'search python')\n"
                    "• Short-term Memory: Remember recent conversation context\n"
                    "• State Telemetry: Live visual AI Reactor Core transitions")

        if any(w in p_lower for w in ["hello", "hi", "hey", "greetings"]):
            return f"Hello, {self.operator_name}. JARVIS systems are online and ready."

        if "thank" in p_lower:
            return f"At your service, {self.operator_name}."

        # Default Intelligent Local Response
        return f"Processed query: '{prompt}'. Systems are operational."

class OpenAIProvider(BaseAIProvider):
    """
    OpenAI API Provider Integration.
    Falls back gracefully to LocalMockProvider if OPENAI_API_KEY is not configured.
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or config.get("ai.openai_api_key")
        self.fallback = LocalMockProvider()
        
        if not self.api_key:
            logger.warning("[OpenAIProvider] OPENAI_API_KEY not configured. Falling back to LocalMockProvider.")

    def generate_response(self, prompt: str, history: List[Dict[str, str]]) -> str:
        if not self.api_key:
            return self.fallback.generate_response(prompt, history)

        try:
            # Simple HTTP / Client fallback if urllib / requests is used
            import urllib.request
            import json

            url = "https://api.openai.com/v1/chat/completions"
            messages = [{"role": "system", "content": "You are JARVIS, a concise, intelligent, professional, and slightly futuristic personal AI desktop assistant. Address the user as Varun when appropriate. Keep responses concise and factual."}]
            
            for h in history:
                messages.append({"role": h.get("role", "user"), "content": h.get("message", "")})
            messages.append({"role": "user", "content": prompt})

            data = json.dumps({"model": config.get("ai.model", "gpt-4o-mini"), "messages": messages, "max_tokens": 150}).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            })

            with urllib.request.urlopen(req, timeout=8) as response:
                res_body = json.loads(response.read().decode("utf-8"))
                return res_body["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error(f"[OpenAIProvider] API Error: {e}. Falling back to local provider.")
            return self.fallback.generate_response(prompt, history)

def get_provider() -> BaseAIProvider:
    """Factory to get configured AI Provider based on configuration."""
    provider_name = config.get("ai.provider", "local").lower()
    if provider_name == "openai" or os.getenv("OPENAI_API_KEY"):
        return OpenAIProvider()
    return LocalMockProvider()
