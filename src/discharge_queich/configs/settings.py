from pathlib import Path
from pydantic import BaseModel

from discharge_queich.configs.database import DatabaseSettings
from discharge_queich.configs.dashboard import DashboardSettings
from discharge_queich.configs.ingestion import IngestionSettings
from discharge_queich.configs.model import ModelSettings
from discharge_queich.configs.scheduler import SchedulerSettings


class Settings(BaseModel):
    database: DatabaseSettings
    dashboard: DashboardSettings
    ingestion: IngestionSettings
    model: ModelSettings
    scheduler: SchedulerSettings