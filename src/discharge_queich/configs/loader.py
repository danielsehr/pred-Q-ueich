from pathlib import Path
import yaml
import os

from discharge_queich.configs.settings import Settings


CONFIG_DIR = Path(__file__).parent / "yaml"

def load_yaml(filename: str | Path) -> dict:
    with open(Path(CONFIG_DIR) / filename, "r") as f:
        return yaml.safe_load(f)


    
def load_settings() -> Settings:

    yaml_config = {
        "database": load_yaml("database.yaml"),
        "dashboard": load_yaml("dashboard.yaml"),
        "ingestion": load_yaml("ingestion.yaml"),
        "model": load_yaml("model.yaml"),
        "scheduler": load_yaml("scheduler.yaml"),
    }
    
    yaml_config["dashboard"]["api_url"] = (
    os.getenv(
        key="DASHBOARD__API_URL",
        default=yaml_config["dashboard"]["api_url"]
        )
    )

    # return Settings.model_validate(yaml_config)
    return Settings(**yaml_config)