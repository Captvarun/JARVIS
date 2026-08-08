from core.logger import logger
from core.state import state
from core.brain.brain import brain
from database.db import init_db

def bootstrap():
    """
    JARVIS System Bootstrap.
    Initializes core services, database, state, and intelligence brain.
    """
    logger.info("Initializing JARVIS System Core...")
    
    # 1. Initialize SQLite Database
    init_db()

    # 2. Initialize App State
    state.set("status", "ONLINE")

    # 3. Initialize Intelligence Brain
    brain.initialize()

    logger.info("JARVIS Bootstrap complete.")
