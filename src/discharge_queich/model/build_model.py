from src.configs import settings
from xgboost import XGBRegressor

hparams = settings.model.xgboost

model = XGBRegressor(
    n_estimators=hparams.n_estimators,
    max_depth=hparams.max_depth,
    learning_rate=hparams.learning_rate,
    # subsample=0.8,
    # colsample_bytree=0.8,
    objective=hparams.objective,
    random_state=hparams.random_state,
    early_stopping_rounds=hparams.early_stopping_rounds
)