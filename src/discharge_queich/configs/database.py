from pydantic import BaseModel


class DatabaseSettings(BaseModel):
    database_url: str
    query_timedelta_days: int
