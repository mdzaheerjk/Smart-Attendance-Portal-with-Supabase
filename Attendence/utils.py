# helper class 

# Attendence/utils.py
from datetime import datetime   # date and time
import pytz  # asia
from .logger import get_logger

logger = get_logger(__name__)

def current_ist_date():
    """Return current date string in Asia/Kolkata as YYYY-MM-DD"""
    try:
        IST = pytz.timezone("Asia/Kolkata")
        return datetime.now(IST).strftime("%Y-%m-%d")
    except Exception:
        logger.exception("Failed to compute IST date")
        # Fallback to UTC date string
        return datetime.now().strftime("%Y-%m-%d")
