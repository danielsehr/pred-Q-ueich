from pydantic_settings import BaseSettings


class JobConfig(BaseSettings):
    name: str
    interval_minutes: int


class SchedulerSettings(BaseSettings):
    jobs: list[JobConfig]