import re
from core.personality.personality import personality
from core.events import events
from core.logger import logger

class PersonalityHandler:
    """
    Parses and dispatches natural language personality commands.
    """
    def handle_command(self, prompt: str) -> str:
        p_lower = prompt.lower().strip()

        # 1. Personality Query
        if any(w in p_lower for w in ["what's your personality", "what is your personality", "show your personality", "current personality"]):
            events.log_emitted.emit("personality", "Querying current personality profile")
            return personality.get_summary()

        # 2. Reset Personality
        if "reset" in p_lower and "personality" in p_lower:
            personality.reset()
            events.log_emitted.emit("personality", "Personality state reset to default COMPANION profile")
            return "Personality state reset to default COMPANION profile."

        # 3. Profile Switching Commands
        profile_matches = {
            "professional": "PROFESSIONAL",
            "companion": "COMPANION",
            "sarcastic": "SARCASTIC",
            "focus": "FOCUS"
        }
        for kw, prof in profile_matches.items():
            if kw in p_lower and ("mode" in p_lower or "profile" in p_lower or "switch" in p_lower):
                personality.set_profile(prof)
                events.log_emitted.emit("personality", f"Switched personality profile to {prof}")
                return f"Switched to {prof} mode."

        # 4. Absolute Set Values (e.g. "set sarcasm to 30%", "sarcasm 40%")
        set_match = re.search(r"(set|turn|change)\s+(humor|sarcasm|empathy|formality|energy|verbosity|confidence)\s+(to|=)?\s*(\d+)", p_lower)
        if set_match:
            param = set_match.group(2)
            val = int(set_match.group(4))
            personality.set(param, val)
            events.log_emitted.emit("personality", f"{param.capitalize()} set to {val}%")
            return f"{param.capitalize()} updated to {val}%."

        # Turn Off Command ("turn sarcasm off")
        off_match = re.search(r"turn\s+(humor|sarcasm|empathy|formality|energy|verbosity)\s+off", p_lower)
        if off_match:
            param = off_match.group(1)
            personality.set(param, 0)
            events.log_emitted.emit("personality", f"{param.capitalize()} turned off (0%)")
            return f"{param.capitalize()} turned off (0%)."

        # 5. Relative Changes (e.g. "reduce sarcasm by 20%", "increase humor by 15%")
        rel_match = re.search(r"(increase|reduce|decrease|lower|raise)\s+(humor|sarcasm|empathy|formality|energy|verbosity|confidence)\s+by\s+(\d+)", p_lower)
        if rel_match:
            action = rel_match.group(1)
            param = rel_match.group(2)
            delta = int(rel_match.group(3))
            if action in ("reduce", "decrease", "lower"):
                delta = -delta
            personality.modify(param, delta)
            events.log_emitted.emit("personality", f"{param.capitalize()} adjusted by {delta:+d}% (Now {personality.get(param)}%)")
            return f"{param.capitalize()} modified to {personality.get(param)}%."

        # 6. Qualitative Natural Commands
        qualitative_rules = [
            (r"(more humorous|increase humor|be funnier)", "humor", 20),
            (r"(less humorous|be less funny)", "humor", -20),
            (r"(more sarcastic)", "sarcasm", 20),
            (r"(less sarcastic|be less sarcastic)", "sarcasm", -20),
            (r"(more formal|be more formal)", "formality", 20),
            (r"(less formal|be less formal)", "formality", -20),
            (r"(more empathetic|be more empathetic)", "empathy", 20),
            (r"(shorter|more concise|shorter answers)", "verbosity", -25),
            (r"(more verbose|longer answers)", "verbosity", 25)
        ]

        for pattern, param, delta in qualitative_rules:
            if re.search(pattern, p_lower):
                personality.modify(param, delta)
                events.log_emitted.emit("personality", f"{param.capitalize()} adjusted to {personality.get(param)}%")
                return f"{param.capitalize()} adjusted to {personality.get(param)}%."

        return f"Personality updated. Current Profile: {personality.active_profile}."
