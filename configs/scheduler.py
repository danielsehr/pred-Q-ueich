from pydantic import BaseModel


# --- Scheduler ----
class JobConfig(BaseModel):
    name: str
    interval_minutes: int


class SchedulerSettings(BaseModel):
    jobs: list[JobConfig]