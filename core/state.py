from typing import Any, Dict
from PySide6.QtCore import QObject
from core.events import events
from core.logger import logger

class AppState(QObject):
    """
    Central Application State Manager for JARVIS.
    Maintains active system modes, status flags, and component configurations.
    """
    def __init__(self):
        super().__init__()
        self._state: Dict[str, Any] = {
            "status": "ONLINE",
            "voice_enabled": False,
            "vision_enabled": False,
            "active_tab": "Dashboard",
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "active_model": "OpenAI / Local HUD"
        }

    def get(self, key: str, default: Any = None) -> Any:
        return self._state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        if self._state.get(key) != value:
            self._state[key] = value
            logger.debug(f"State changed: {key} -> {value}")
            events.state_updated.emit(key, value)

    def to_dict(self) -> Dict[str, Any]:
        return self._state.copy()

# Global singleton app state
state = AppState()
