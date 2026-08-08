import sqlite3
from pathlib import Path
from typing import List, Dict
from core.logger import logger

DB_PATH = Path(__file__).parent / "jarvis.db"

def init_db():
    """Initialize SQLite database for JARVIS."""
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

        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {DB_PATH}")
    except Exception as e:
        logger.error(f"Failed to initialize SQLite database: {e}")

def get_connection():
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
