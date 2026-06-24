from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    database_url: str
    query_timedelta_days: int
