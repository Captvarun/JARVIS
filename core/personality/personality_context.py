from typing import Dict, Any, Optional

class PersonalityContextManager:
    """
    Context-Aware Personality & Temporary Override Manager.
    Calculates effective runtime parameters during SERIOUS, DISTRESS, SYSTEM_ERROR,
    or CRITICAL contexts and manages conversational overrides without permanently modifying database settings.
    """
    def __init__(self):
        self.context_tag: str = "NORMAL"
        self.temp_overrides: Dict[str, Any] = {}

    def set_context(self, tag: str):
        """Sets current situational context tag."""
        self.context_tag = tag.upper()

    def set_temp_override(self, param: str, val: Any):
        """Sets temporary conversational override for current session."""
        self.temp_overrides[param.lower()] = val

    def clear_temp_overrides(self):
        """Clears temporary conversational overrides."""
        self.temp_overrides.clear()
        self.context_tag = "NORMAL"

    def get_effective_params(self, base_params: Dict[str, int]) -> Dict[str, int]:
        """
        Computes effective runtime parameters considering context suppression
        and temporary overrides.
        """
        effective = base_params.copy()

        # Context-Aware Suppression Rules
        if self.context_tag in ("SERIOUS", "DISTRESS", "SYSTEM_ERROR", "CRITICAL"):
            effective["humor"] = min(effective["humor"], 5)
            effective["sarcasm"] = 0
            if self.context_tag in ("DISTRESS", "CRITICAL"):
                effective["empathy"] = max(effective["empathy"], 90)
                effective["friendliness"] = max(effective["friendliness"], 90)

        # Apply Temporary Conversational Overrides
        if "suppress_humor" in self.temp_overrides and self.temp_overrides["suppress_humor"]:
            effective["humor"] = 0
        if "suppress_sarcasm" in self.temp_overrides and self.temp_overrides["suppress_sarcasm"]:
            effective["sarcasm"] = 0
        if "verbosity" in self.temp_overrides:
            effective["verbosity"] = self.temp_overrides["verbosity"]
        if "formality" in self.temp_overrides:
            effective["formality"] = self.temp_overrides["formality"]

        return effective
