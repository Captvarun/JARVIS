from typing import Dict, Any

PROFILES: Dict[str, Dict[str, int]] = {
    "PROFESSIONAL": {
        "humor": 20,
        "sarcasm": 5,
        "empathy": 70,
        "formality": 85,
        "energy": 50,
        "verbosity": 45,
        "confidence": 90,
        "friendliness": 65
    },
    "COMPANION": {
        "humor": 70,
        "sarcasm": 30,
        "empathy": 90,
        "formality": 30,
        "energy": 70,
        "verbosity": 60,
        "confidence": 90,
        "friendliness": 90
    },
    "SARCASTIC": {
        "humor": 85,
        "sarcasm": 80,
        "empathy": 70,
        "formality": 20,
        "energy": 75,
        "verbosity": 50,
        "confidence": 95,
        "friendliness": 75
    },
    "FOCUS": {
        "humor": 5,
        "sarcasm": 0,
        "empathy": 60,
        "formality": 65,
        "energy": 55,
        "verbosity": 25,
        "confidence": 95,
        "friendliness": 60
    }
}
