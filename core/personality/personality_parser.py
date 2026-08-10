import re
from typing import Dict, Any, Optional

class PersonalityParser:
    """
    Robust Natural Language Parser for Personality Control Commands.
    Supports absolute, relative, qualitative, profile, query, reset, and temporary override requests.
    """
    PARAMS = ["humor", "sarcasm", "empathy", "formality", "energy", "verbosity", "confidence", "friendliness"]

    def parse(self, prompt: str) -> Dict[str, Any]:
        p = prompt.lower().strip()
        res = {"type": "UNKNOWN", "param": None, "val": None, "profile": None, "raw": prompt}

        # 1. Personality Queries
        if any(w in p for w in [
            "what's your personality", "what is your personality", "show your personality",
            "current settings", "current personality", "how sarcastic are you", "how humorous are you",
            "how formal are you", "sarcasm level", "humor level", "empathy level", "formality level",
            "energy level", "verbosity level", "confidence level", "friendliness level", "personality parameters"
        ]) and not ("set" in p or "change" in p or "increase" in p or "reduce" in p):
            res["type"] = "GET_PERSONALITY"
            for param in self.PARAMS:
                if param in p:
                    res["param"] = param
                    break
            return res

        # 2. Reset / Default Personality
        if ("reset" in p and "personality" in p) or "use default personality" in p or "use your default personality" in p:
            res["type"] = "RESET_PERSONALITY"
            return res

        # 3. Profile Switching
        profiles = {
            "professional": "PROFESSIONAL",
            "companion": "COMPANION",
            "sarcastic": "SARCASTIC",
            "focus": "FOCUS"
        }
        for kw, prof_name in profiles.items():
            if kw in p and ("mode" in p or "profile" in p or "switch" in p or "go into" in p or "use" in p):
                res["type"] = "SET_PERSONALITY_PROFILE"
                res["profile"] = prof_name
                return res

        # 4. Temporary Conversational Overrides
        if any(w in p for w in ["be serious for now", "stop joking for now", "don't be sarcastic", "dont be sarcastic"]):
            res["type"] = "TEMP_OVERRIDE"
            res["override_type"] = "SERIOUS"
            return res
        if "keep it short" in p or "keep answers short" in p:
            res["type"] = "TEMP_OVERRIDE"
            res["override_type"] = "CONCISE"
            return res
        if "explain in detail" in p or "explain this in detail" in p:
            res["type"] = "TEMP_OVERRIDE"
            res["override_type"] = "VERBOSE"
            return res

        # 5. Absolute Set Command ("set sarcasm to 30%", "set your humor level to 80%", "make yourself 50% formal")
        set_match = re.search(r"(set|change|make yourself)\s+(your\s+)?(humor|sarcasm|empathy|formality|energy|verbosity|confidence|friendliness)(\s+level)?\s+(to|=)?\s*(\d+)", p)
        if set_match:
            res["type"] = "MODIFY_PERSONALITY"
            res["mode"] = "ABSOLUTE"
            res["param"] = set_match.group(3)
            res["val"] = int(set_match.group(6))
            return res

        # Turn Off Command ("turn sarcasm off")
        off_match = re.search(r"turn\s+(humor|sarcasm|empathy|formality|energy|verbosity|confidence|friendliness)\s+off", p)
        if off_match:
            res["type"] = "MODIFY_PERSONALITY"
            res["mode"] = "ABSOLUTE"
            res["param"] = off_match.group(1)
            res["val"] = 0
            return res

        # 6. Relative Command ("reduce sarcasm by 20%", "increase humor by 15%")
        rel_match = re.search(r"(increase|reduce|decrease|lower|raise)\s+(your\s+)?(humor|sarcasm|empathy|formality|energy|verbosity|confidence|friendliness)(\s+level)?\s+by\s+(\d+)", p)
        if rel_match:
            action = rel_match.group(1)
            param = rel_match.group(3)
            delta = int(rel_match.group(5))
            if action in ("reduce", "decrease", "lower"):
                delta = -delta
            res["type"] = "MODIFY_PERSONALITY"
            res["mode"] = "RELATIVE"
            res["param"] = param
            res["val"] = delta
            return res

        # 7. Qualitative Commands ("be more humorous", "make yourself less sarcastic", "be more friendly", etc.)
        qualitative_rules = [
            (r"(more humorous|increase humor|be funnier|more funny)", "humor", 20),
            (r"(less humorous|be less funny|reduce humor)", "humor", -20),
            (r"(more sarcastic|make yourself more sarcastic)", "sarcasm", 20),
            (r"(less sarcastic|make yourself less sarcastic|stop being sarcastic)", "sarcasm", -20),
            (r"(more formal|be more formal)", "formality", 20),
            (r"(less formal|stop being so formal|be less formal)", "formality", -20),
            (r"(more empathetic|increase your empathy|more empathy)", "empathy", 20),
            (r"(more friendly|be more friendly)", "friendliness", 20),
            (r"(less friendly|be less friendly)", "friendliness", -20),
            (r"(shorter|more concise|make your answers shorter)", "verbosity", -25),
            (r"(more detailed|be more detailed|more verbose)", "verbosity", 25),
            (r"(more confident|speak with more confidence)", "confidence", 20),
            (r"(calm down|be more energetic)", "energy", -20 if "calm" in p else 20)
        ]

        for pattern, param, delta in qualitative_rules:
            if re.search(pattern, p):
                res["type"] = "MODIFY_PERSONALITY"
                res["mode"] = "RELATIVE"
                res["param"] = param
                res["val"] = delta
                return res

        return res
