from apscheduler.schedulers.blocking import BlockingScheduler

from configs import settings
from src.utils.logger import logger
from src.scheduler.registry import JOB_REGISTRY


def run_initial_ingestion():
    logger.info("[INIT] Running initial ingestion")
    
    for job in settings.scheduler.jobs:
        func = JOB_REGISTRY[job.name]
        
        logger.info("[INIT] %s", job.name)
        func()


def start_scheduler():
    scheduler = BlockingScheduler()
    
    for job in settings.scheduler.jobs:
        func = JOB_REGISTRY[job.name]
        
        scheduler.add_job(
            func=func,
            trigger="interval",
            minutes=job.interval_minutes,
            max_instances=1,
            coalesce=True,
            id=job.name,
        )

    logger.info("[SCHEDULER] Running...")
    scheduler.start()


if __name__ == "__main__":
    run_initial_ingestion()
    start_scheduler()