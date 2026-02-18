import logging
import sys  # line number
import os  # files

# Create logs folder if not exists
LOG_DIR = "logs"

os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name="attendence"):
    """
    Create and return a logger that logs to both console and logs/app.log.
    Prevents duplicate handlers and keeps formatting consistent.
    """
    logger = logging.getLogger(name)

    # If handlers already exist, return existing logger
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Prepare formatter (single definition)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | "
        "%(filename)s:%(lineno)d | %(funcName)s() | %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # File handler
    file_handler = logging.FileHandler(
        os.path.join(LOG_DIR, "app.log"),
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # Register handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.propagate = False
    return logger
