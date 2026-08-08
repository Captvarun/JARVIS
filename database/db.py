import sqlite3
from pathlib import Path
from typing import List, Dict, Any
from core.logger import logger

DB_PATH = Path(__file__).parent / "jarvis.db"
_db_initialized = False

def init_db():
    """Initialize SQLite database for JARVIS."""
    global _db_initialized
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # System settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        # Conversation history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                role TEXT NOT NULL,
                message TEXT NOT NULL
            )
        """)

        # Personality state table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS personality_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()
        _db_initialized = True
        logger.info(f"Database initialized at {DB_PATH}")
    except Exception as e:
        logger.error(f"Failed to initialize SQLite database: {e}")

def get_connection():
    if not _db_initialized:
        init_db()
    return sqlite3.connect(DB_PATH)

def save_message(role: str, message: str):
    """Saves a conversation turn to SQLite history."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO conversation_history (role, message) VALUES (?, ?)", (role, message))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to save message to SQLite database: {e}")

def get_recent_history(limit: int = 10) -> List[Dict[str, str]]:
    """Retrieves recent conversation turns from SQLite database."""
    history = []
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT role, message FROM conversation_history ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        for r, m in reversed(rows):
            history.append({"role": r, "message": m})
    except Exception as e:
        logger.error(f"Failed to fetch conversation history: {e}")
    return history

def save_personality_db(settings: Dict[str, Any]):
    """Persists personality parameters to SQLite database."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        for k, v in settings.items():
            cursor.execute("INSERT OR REPLACE INTO personality_state (key, value) VALUES (?, ?)", (k, str(v)))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to save personality to DB: {e}")

def load_personality_db() -> Dict[str, Any]:
    """Loads personality parameters from SQLite database."""
    settings = {}
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM personality_state")
        rows = cursor.fetchall()
        conn.close()
        for k, v in rows:
            if str(v).isdigit():
                settings[k] = int(v)
            else:
                settings[k] = v
    except Exception as e:
        logger.error(f"Failed to load personality from DB: {e}")
    return settings
