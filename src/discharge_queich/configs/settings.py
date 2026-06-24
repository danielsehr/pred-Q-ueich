from pathlib import Path
import yaml
from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    PydanticBaseSettingsSource,
    YamlConfigSettingsSource
    )

from discharge_queich.configs.database import DatabaseSettings
from discharge_queich.configs.dashboard import DashboardSettings
from discharge_queich.configs.ingestion import IngestionSettings
from discharge_queich.configs.model import ModelSettings
from discharge_queich.configs.scheduler import SchedulerSettings


class Settings(BaseSettings):
    
    database: DatabaseSettings
    dashboard: DashboardSettings
    ingestion: IngestionSettings
    model: ModelSettings
    scheduler: SchedulerSettings
    
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        extra="ignore"
    )