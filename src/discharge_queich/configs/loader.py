from pathlib import Path

import yaml

from discharge_queich.configs.settings import Settings
from discharge_queich.configs.database import DatabaseSettings
from discharge_queich.configs.dashboard import DashboardSettings
from discharge_queich.configs.ingestion import IngestionSettings
from discharge_queich.configs.model import ModelSettings
from discharge_queich.configs.scheduler import SchedulerSettings


CONFIG_DIR = Path(__file__).parent / "yaml"

def load_yaml(filename: str) -> dict:
    with open(CONFIG_DIR / filename, "r") as f:
        return yaml.safe_load(f)
    
    
def load_settings() -> Settings:
    
    return Settings(
        database=DatabaseSettings.model_validate(
            load_yaml("database.yaml")
        ),
        dashboard=DashboardSettings.model_validate(
            load_yaml("dashboard.yaml")
        ),
        ingestion=IngestionSettings.model_validate(
            load_yaml("ingestion.yaml")
        ),
        model=ModelSettings.model_validate(
            load_yaml("model.yaml")    
        ),
        scheduler=SchedulerSettings.model_validate(
            load_yaml("scheduler.yaml")
        )
    )