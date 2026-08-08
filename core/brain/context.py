from typing import List, Dict
from database.db import save_message, get_recent_history

class ContextManager:
    """
    Manages bounded short-term conversation context.
    Prevents context buffer from expanding indefinitely while retaining recent dialogue turns.
    """
    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self._buffer: List[Dict[str, str]] = []
        self._load_from_db()

    def _load_from_db(self):
        self._buffer = get_recent_history(self.max_turns)

    def add_turn(self, role: str, message: str):
        """Adds a new conversation turn to short-term memory and database."""
        turn = {"role": role, "message": message}
        self._buffer.append(turn)
        
        # Enforce bounded context length
        if len(self._buffer) > self.max_turns:
            self._buffer.pop(0)

        # Persist to SQLite
        save_message(role, message)

    def get_history(self) -> List[Dict[str, str]]:
        return self._buffer.copy()
