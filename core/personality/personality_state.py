from typing import Dict, Any
from core.logger import logger
from database.db import save_personality_db, load_personality_db
from core.personality.personality_profiles import PROFILES

class PersonalityState:
    """
    Centralized Personality State Store.
    Manages 8 personality parameters (0–100) and profile presets.
    Persists settings to SQLite database.
    """
    DEFAULTS: Dict[str, int] = {
        "humor": 65,
        "sarcasm": 30,
        "empathy": 85,
        "formality": 35,
        "energy": 70,
        "verbosity": 55,
        "confidence": 90,
        "friendliness": 80
    }

    def __init__(self):
        self._state: Dict[str, int] = self.DEFAULTS.copy()
        self.active_profile: str = "COMPANION"
        self._load()

    def _load(self):
        try:
            saved = load_personality_db()
            if saved:
                for k in self.DEFAULTS:
                    if k in saved:
                        self._state[k] = self._clamp(saved[k])
                if "active_profile" in saved and isinstance(saved["active_profile"], str):
                    self.active_profile = saved["active_profile"]
                logger.info(f"[PersonalityState] Loaded state from SQLite database (Profile: {self.active_profile})")
        except Exception as e:
            logger.error(f"[PersonalityState] Error loading state: {e}")

    def save(self):
        try:
            to_save = self._state.copy()
            to_save["active_profile"] = self.active_profile
            save_personality_db(to_save)
        except Exception as e:
            logger.error(f"[PersonalityState] Error saving state: {e}")

    def _clamp(self, val: Any) -> int:
        try:
            v = int(val)
            return max(0, min(100, v))
        except (ValueError, TypeError):
            return 50

    def get(self, param: str) -> int:
        return self._state.get(param.lower(), 50)

    def set(self, param: str, val: int):
        p_lower = param.lower()
        if p_lower in self._state:
            old_v = self._state[p_lower]
            new_v = self._clamp(val)
            self._state[p_lower] = new_v
            self.active_profile = "CUSTOM"
            self.save()
            logger.info(f"[PersonalityState] Set {p_lower}: {old_v}% -> {new_v}% (Profile: CUSTOM)")

    def modify(self, param: str, delta: int):
        p_lower = param.lower()
        if p_lower in self._state:
            self.set(p_lower, self._state[p_lower] + delta)

    def set_profile(self, profile_name: str) -> bool:
        name_upper = profile_name.upper()
        if name_upper in PROFILES:
            preset = PROFILES[name_upper]
            for k, v in preset.items():
                self._state[k] = v
            self.active_profile = name_upper
            self.save()
            logger.info(f"[PersonalityState] Applied profile preset: {name_upper}")
            return True
        return False

    def reset(self):
        for k, v in self.DEFAULTS.items():
            self._state[k] = v
        self.active_profile = "COMPANION"
        self.save()
        logger.info("[PersonalityState] Reset personality state to default COMPANION profile.")

    def get_summary(self) -> str:
        lines = [f"JARVIS PERSONALITY\n", f"Profile: {self.active_profile}\n"]
        for k, v in self._state.items():
            lines.append(f"{k.capitalize():<13} {v}%")
        return "\n".join(lines)

    def get_all_params(self) -> Dict[str, int]:
        return self._state.copy()
