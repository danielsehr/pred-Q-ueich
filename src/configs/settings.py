from pathlib import Path
from pydantic import BaseModel

from configs.database import DatabaseSettings
from configs.dashboard import DashboardSettings
from configs.ingestion import IngestionSettings
from configs.model import ModelSettings
from configs.scheduler import SchedulerSettings


class Settings(BaseModel):
    database: DatabaseSettings
    dashboard: DashboardSettings
    ingestion: IngestionSettings
    model: ModelSettings
    scheduler: SchedulerSettings