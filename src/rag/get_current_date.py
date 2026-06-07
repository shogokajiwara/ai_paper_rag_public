import logging
logger = logging.getLogger(__name__)
logger.propagate = True

from datetime import datetime

def get_current_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")