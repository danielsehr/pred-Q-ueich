from apscheduler.schedulers.blocking import BlockingScheduler
from scheduler.config import JOBS


def run_initial_ingestion():
    print("[INIT] Running intial ingestion")
    
    for job in JOBS:
        print(f"[INIT] {job['name']}")
        job["func"]()


def start_scheduler():
    scheduler = BlockingScheduler()

    for job in JOBS:
        scheduler.add_job(
            job["func"],
            trigger="interval",
            minutes=job["interval_minutes"],
            max_instances=1,
            coalesce=True,
            id=job["name"],
        )

    print("[SCHEDULER] Running...")
    scheduler.start()


if __name__ == "__main__":
    run_initial_ingestion()
    start_scheduler()