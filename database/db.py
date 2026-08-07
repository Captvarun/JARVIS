import sqlite3
from pathlib import Path
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

        # Logs / Conversations table
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
