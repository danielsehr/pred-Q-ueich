from pathlib import Path

# --- build_model.py ---
hparams = {
    "n_estimators": 10000,
    "max_depth": 6,
    "learning_rate": 0.01,
    # subsample=0.8,
    # colsample_bytree=0.8,
    "objective": 'reg:squarederror',
    "random_state":42,
    "early_stopping_rounds": 150
}


# --- features.py ---
shift_vars = [
    "discharge", "precip_mean"
    ]

sum_vars = [
    "precip_mean"
    ]

# Lags in lag * timestamp (15 min)
shift_lags = [
    1, 2, 3, 4, 8, 12, 24, 48
   # , 96
    ]

# Delay in lag * timestamp (15 min)
delays = [
    1, 2, 3, 4, 8, 12, 24, 48
]

# Lags in lag * timestamp (15 min)
sum_lags = [
    1, 2, 3, 4, 8, 12, 24, 48
    # , 96
    ]

# Timesteps of inference. 1 -> 15 min
inference_steps = 1


# --- inference.py ---
# MODEL_PATH = Path("models/xgb_model_discharge_precip_MA.json")
MODEL_PATH = Path("models/xgb_model_discharge_precip_hampel_ewm.json")