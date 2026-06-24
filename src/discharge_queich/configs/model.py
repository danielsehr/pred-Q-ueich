from pathlib import Path
from pydantic_settings import BaseSettings


# --- Model ---
class XGBoostSettings(BaseSettings):
    n_estimators: int = 10_000
    max_depth: int = 6
    learning_rate: float = 0.01
    objective: str = "reg:squarederror"
    random_state: int = 42
    early_stopping_rounds: int = 150
    
    
class FeatureEngineeringSettings(BaseSettings):
    shift_vars: list[str] = [
        "discharge",
        "precip_mean",
    ]

    sum_vars: list[str] = [
        "precip_mean",
    ]

    shift_lags: list[int] = [
        1, 2, 3, 4, 8, 12, 24, 48
    ]

    delays: list[int] = [
        1, 2, 3, 4, 8, 12, 24, 48
    ]

    sum_lags: list[int] = [
        1, 2, 3, 4, 8, 12, 24, 48
    ]


class InferenceSettings(BaseSettings):
    steps: int = 1
    model_path: Path = Path(
        "models/xgb_model_discharge_precip_hampel_ewm.json"
    )


class ModelSettings(BaseSettings):
    xgboost: XGBoostSettings = XGBoostSettings()
    features: FeatureEngineeringSettings = FeatureEngineeringSettings()
    inference: InferenceSettings = InferenceSettings()