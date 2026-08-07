import logging
import sys

class HUDFormatter(logging.Formatter):
    """Custom formatter with futuristic HUD colored level tags and clean timestamps."""
    
    CYAN = "\x1b[36;20m"
    GREEN = "\x1b[32;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"
    
    FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"

    FORMATS = {
        logging.DEBUG: CYAN + FORMAT + RESET,
        logging.INFO: GREEN + FORMAT + RESET,
        logging.WARNING: YELLOW + FORMAT + RESET,
        logging.ERROR: RED + FORMAT + RESET,
        logging.CRITICAL: BOLD_RED + FORMAT + RESET
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.FORMAT)
        formatter = logging.Formatter(log_fmt, datefmt="%H:%M:%S")
        return formatter.format(record)

def setup_logger(name: str = "JARVIS") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(HUDFormatter())
        logger.addHandler(ch)
    return logger

logger = setup_logger()
