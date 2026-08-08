from typing import Dict, Any
from core.logger import logger
from database.db import save_personality_db, load_personality_db

class PersonalityState:
    """
    Centralized Personality State Manager for JARVIS.
    Manages 7 parameters (0-100) and profile presets.
    Persists settings to SQLite database.
    """
    DEFAULTS = {
        "humor": 65,
        "sarcasm": 30,
        "empathy": 85,
        "formality": 35,
        "energy": 70,
        "verbosity": 55,
        "confidence": 90
    }

    PROFILES = {
        "PROFESSIONAL": {"humor": 15, "sarcasm": 0,  "empathy": 70, "formality": 90, "energy": 60, "verbosity": 30, "confidence": 95},
        "COMPANION":    {"humor": 65, "sarcasm": 30, "empathy": 85, "formality": 35, "energy": 70, "verbosity": 55, "confidence": 90},
        "SARCASTIC":   {"humor": 85, "sarcasm": 85, "empathy": 40, "formality": 20, "energy": 80, "verbosity": 60, "confidence": 95},
        "FOCUS":        {"humor": 0,  "sarcasm": 0,  "empathy": 50, "formality": 60, "energy": 50, "verbosity": 20, "confidence": 90}
    }

    def __init__(self):
        self._state: Dict[str, int] = self.DEFAULTS.copy()
        self.active_profile: str = "COMPANION"
        self._load()

    def _load(self):
        saved = load_personality_db()
        if saved:
            for k, v in saved.items():
                if k in self._state:
                    self._state[k] = self._clamp(v)
            self.active_profile = saved.get("active_profile_name", "CUSTOM")
            logger.info(f"[PersonalityState] Loaded personality state from database (Profile: {self.active_profile})")

    def _save(self):
        to_save = self._state.copy()
        save_personality_db(to_save)

    def _clamp(self, val: int) -> int:
        return max(0, min(100, int(val)))

    def get(self, param: str) -> int:
        return self._state.get(param, 50)

    def set(self, param: str, val: int):
        if param in self._state:
            old_v = self._state[param]
            new_v = self._clamp(val)
            self._state[param] = new_v
            self.active_profile = "CUSTOM"
            self._save()
            logger.info(f"[PersonalityState] Set {param}: {old_v}% -> {new_v}% (Profile: CUSTOM)")

    def modify(self, param: str, delta: int):
        if param in self._state:
            self.set(param, self._state[param] + delta)

    def set_profile(self, profile_name: str) -> bool:
        name_upper = profile_name.upper()
        if name_upper in self.PROFILES:
            preset = self.PROFILES[name_upper]
            for k, v in preset.items():
                self._state[k] = v
            self.active_profile = name_upper
            self._save()
            logger.info(f"[PersonalityState] Switched personality profile to {name_upper}")
            return True
        return False

    def reset(self):
        for k, v in self.DEFAULTS.items():
            self._state[k] = v
        self.active_profile = "COMPANION"
        self._save()
        logger.info("[PersonalityState] Reset personality to default COMPANION profile.")

    def get_summary(self) -> str:
        lines = ["JARVIS PERSONALITY PROFILE\n"]
        for k, v in self._state.items():
            lines.append(f"{k.capitalize():<12} {v}%")
        lines.append(f"\nActive Profile: {self.active_profile}")
        return "\n".join(lines)

    def get_effective_humor_and_sarcasm(self, context_tag: str = "NORMAL") -> tuple[int, int]:
        """
        Context-Aware Humor calculation.
        Reduces/suppresses humor & sarcasm in SERIOUS, DISTRESS, or ERROR contexts.
        """
        base_h = self._state["humor"]
        base_s = self._state["sarcasm"]

        if context_tag in ("SERIOUS", "DISTRESS", "ERROR", "CRITICAL"):
            return (0, 0)
        return (base_h, base_s)

# Global Personality Singleton
personality = PersonalityState()
