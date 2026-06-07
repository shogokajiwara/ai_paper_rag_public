import datetime
import requests
import logging
logger = logging.getLogger(__name__)


def run_task() -> int:
    try:
        logger.critical("run_task started")
        r = requests.post("http://knowledgebase:8000/update")
        r.raise_for_status()
        now = datetime.datetime.now().isoformat()
        logger.critical(f"run_task executed at {now}")
        return 0

    except Exception as e:
        logger.critical(f"run_task.py error: {e}")
        return 1
