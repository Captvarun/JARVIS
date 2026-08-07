from core.logger import logger
from core.state import state
from database.db import init_db

def bootstrap():
    """
    JARVIS System Bootstrap.
    Initializes core services, database, state, and logging before UI launch.
    """
    logger.info("Initializing JARVIS System Core...")
    
    # 1. Initialize SQLite Database
    init_db()

    # 2. Initialize App State
    state.set("status", "ONLINE")

    logger.info("JARVIS Bootstrap complete.")
