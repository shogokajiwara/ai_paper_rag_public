import yaml
import logging.config

with open("/config/logging.yml", "r") as f:
    config = yaml.safe_load(f)
logging.config.dictConfig(config)

logger = logging.getLogger(__name__)

from apscheduler.schedulers.blocking import BlockingScheduler
from run_task import run_task

scheduler: BlockingScheduler = BlockingScheduler()

def cron(s: str) -> dict[str, str]:
    minute, hour, day, month, dow = s.split()
    return dict(
        minute=minute,
        hour=hour,
        day=day,
        month=month,
        day_of_week=dow
    )

scheduler.add_job(run_task, 'cron', **cron("43 12 * * *"))

if __name__ == "__main__":
    scheduler.start()
