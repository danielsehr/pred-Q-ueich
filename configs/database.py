from pydantic import BaseModel


class DatabaseSettings(BaseModel):
    query_timedelta_days: int
