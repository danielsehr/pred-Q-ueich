from apscheduler.schedulers.blocking import BlockingScheduler

from discharge_queich.configs import settings
from discharge_queich.utils.logger import logger
from discharge_queich.database.init_db import initiate_database
from discharge_queich.scheduler.registry import JOB_REGISTRY


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
    initiate_database()
        
    run_initial_ingestion()
    
    start_scheduler()