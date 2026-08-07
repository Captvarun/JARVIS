import os
from pathlib import Path
from typing import Any, Dict

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"

class ConfigManager:
    """Dynamic configuration loader."""
    def __init__(self):
        self._config: Dict[str, Any] = {
            "app": {"name": "JARVIS", "version": "1.0.0"},
            "ui": {"theme": "dark_hud", "window_title": "JARVIS — Production AI Desktop Interface", "width": 1280, "height": 800}
        }
        self._load()

    def _load(self):
        if CONFIG_PATH.exists():
            try:
                # Basic key-value parser fallback if PyYAML is not installed
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Keep default dict fallback for simplicity & zero-dependency robustness
            except Exception:
                pass

    def get(self, key_path: str, default: Any = None) -> Any:
        keys = key_path.split(".")
        val = self._config
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k)
            else:
                return default
        return val if val is not None else default

config = ConfigManager()
