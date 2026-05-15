# --- build_model.py ---
hparams = {
    "n_estimators": 10000,
    "max_depth": 3,
    "learning_rate": 0.01,
    # subsample=0.8,
    # colsample_bytree=0.8,
    "objective": 'reg:squarederror',
    "random_state":42,
    "early_stopping_rounds": 50
}


# --- features.py ---
shift_vars = [
    "pr", "temp", "pet", "discharge"
    ]

sum_vars = [
    "pr", "discharge"
    ]

# Lags in lag * timestamp (15 min)
shift_lags = [
    1, 2, 4, 8, 12, 24, 48, 96
    ]

# Lags in days
sum_lags = [
    3, 7, 14, 21, 28, 35, 42, 56
    ]

# Timesteps of inference. 1 -> 15 min
inference_steps = 1