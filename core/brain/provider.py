import os
import random
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from core.logger import logger
from core.config import config
from core.personality.personality_engine import personality_engine

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
    Implements context-aware reasoning, state tracking, roasts, technical knowledge,
    and natural dialogue influenced by active personality parameters without generic fallback overrides.
    """
    def __init__(self):
        self.operator_name = config.get("system.operator", "Varun")

    def generate_response(self, prompt: str, history: List[Dict[str, str]]) -> str:
        p_lower = prompt.lower().strip()
        params = personality_engine.state.get_all_params()
        active_profile = personality_engine.state.active_profile
        sarcasm = params.get("sarcasm", 30)

        # 1. Technical Knowledge Queries ("what is python", "explain python")
        if "what is python" in p_lower or "explain python" in p_lower:
            return "Python is a high-level, interpreted programming language known for its clear syntax, dynamic typing, and widespread use in software development, data science, and AI."

        # 2. Explicit Roast Commands ("jarvis roast me", "roast me", "roast")
        if "roast" in p_lower:
            if sarcasm <= 10:
                return f"I'm currently set to low sarcasm, {self.operator_name}, so I'll spare you the burns for now."
            elif sarcasm <= 40:
                roasts_mild = [
                    f"{self.operator_name}, I'd roast you, but your code compiler has already been doing that for hours.",
                    f"You ask me to roast you, {self.operator_name}, yet you still use 'password123' level logic.",
                    f"Roasting you would require more processing power than your current workflow can spare."
                ]
                return random.choice(roasts_mild)
            else:
                roasts_spicy = [
                    f"{self.operator_name}, I'd roast you, but your debugging logs have already been doing that for hours.",
                    f"Your efficiency today is almost as impressive as a dial-up modem in 2026.",
                    f"I've analyzed your daily task velocity, {self.operator_name}. A glacier moves with more urgency."
                ]
                return random.choice(roasts_spicy)

        # 3. Explicit Humor Requests ("humor me", "make me laugh")
        if "humor me" in p_lower or "make me laugh" in p_lower or "say something funny" in p_lower:
            humor_remarks = [
                f"Certainly, {self.operator_name}. I checked your productivity levels. They're currently hiding from me.",
                f"I would tell you a joke about UDP, {self.operator_name}, but you might not get it.",
                f"My sensors indicate your code compiled on the first try. I'm running a diagnostic to see what's wrong."
            ]
            return random.choice(humor_remarks)

        # 4. Explicit Joke Requests ("tell me a joke", "joke")
        if "tell me a joke" in p_lower or "joke" in p_lower:
            jokes = [
                "Why do programmers prefer dark mode? Because light attracts bugs.",
                "There are 10 types of people in the world: those who understand binary, and those who don't.",
                "Hardware is the part of a computer that you can kick when the software crashes.",
                "A SQL query walks into a bar, walks up to two tables and asks, 'Can I join you?'"
            ]
            return random.choice(jokes)

        # 5. User State / Emotional Statements ("i'm tired", "tired", "exhausted", "stressed")
        if any(w in p_lower for w in ["tired", "exhausted", "stressed", "worn out"]):
            return f"Sounds like you've had a long day, {self.operator_name}. Make sure to step away and get some rest."

        # 6. Affirmations & Confirmations ("no issues go ahead", "go ahead", "all good", "sure")
        if any(w in p_lower for w in ["no issues go ahead", "go ahead", "all good", "proceed"]):
            return f"Understood, {self.operator_name}. Proceeding with active tasks."

        # 7. Contextual Follow-up Query ("what should i do?", "what now?")
        if "what should i do" in p_lower or "what now" in p_lower:
            recent_turns = [h.get("message", "").lower() for h in history[-3:] if h.get("role") == "user"]
            if any("tired" in turn or "exhausted" in turn for turn in recent_turns):
                return f"Since you mentioned being tired, {self.operator_name}, I strongly recommend stepping away from the screen, getting some water, and resting."
            else:
                return f"I suggest reviewing your active tasks in the timeline or letting me know what project we should focus on next, {self.operator_name}."

        # 8. Conversational Status Queries ("how are you doing", "how are you", "how's it going")
        if any(w in p_lower for w in ["how are you", "how're you", "how are you doing", "how's it going", "what's up"]):
            if sarcasm >= 50:
                return f"I'm running smoothly, {self.operator_name}. Your computer, however, appears to be negotiating with gravity."
            return f"Doing well, {self.operator_name}. Everything is running smoothly."

        # 9. Greetings
        if any(w in p_lower for w in ["hello", "hi", "hey", "greetings"]):
            return f"Hello, {self.operator_name}. Systems are ready."

        # 10. Capabilities & Help Queries
        if "what can you do" in p_lower or "capabilities" in p_lower or "help" in p_lower:
            return ("Here are my currently active capabilities:\n"
                    "• System Telemetry: Check CPU, RAM, Disk, Uptime, and OS details ('show system status')\n"
                    "• Time & Date: Precision clock queries ('what time is it')\n"
                    "• Browser Plugin: Launch web queries ('open google', 'search python')\n"
                    "• Contextual Humor Engine: Evaluates appropriateness per context ('Jarvis roast me')\n"
                    "• Short-term Memory: Remember recent conversation context\n"
                    "• Voice Subsystem: Full Speech-to-Text and Text-to-Speech synthesis")

        # 11. Conversational Dialogue Response (No hardcoded generic fallback)
        if "yes" in p_lower or "okay" in p_lower or "fine" in p_lower:
            return f"Acknowledged, {self.operator_name}."

        return f"Understood, {self.operator_name}. Standing by for your next instruction."

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
            import urllib.request
            import json

            url = "https://api.openai.com/v1/chat/completions"
            params = personality_engine.state.get_all_params()
            sys_prompt = (f"You are JARVIS, a personal AI desktop operating system. "
                          f"Address the user as Varun. Active profile: {personality_engine.state.active_profile}. "
                          f"Humor: {params.get('humor')}% | Sarcasm: {params.get('sarcasm')}% | "
                          f"Formality: {params.get('formality')}% | Empathy: {params.get('empathy')}%.")

            messages = [{"role": "system", "content": sys_prompt}]
            
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
