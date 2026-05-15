import numpy as np
import pandas as pd



def add_time_transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.index = pd.to_datetime(df.index)

    # Day of year transform
    df["doy_sin"] = np.sin(2 * np.pi * df.index.dayofyear / 365)
    df["doy_cos"] = np.cos(2 * np.pi * df.index.dayofyear / 365)
    
    # Minute of day transform
    minutes_of_day = (df.index.hour * 60 + df.index.minute)
    df["mod_sin"] = np.sin(2 * np.pi * minutes_of_day / (24 * 60))
    df["mod_cos"] = np.cos(2 * np.pi * minutes_of_day / (24 * 60))

    return df


def add_lag_features(
    df: pd.DataFrame, 
    lag_vars: list[str] = ["pr", "temp", "pet", "discharge"],
    lags: list[int] = [1, 2, 4, 8, 12, 24, 48, 96]
    ) -> pd.DataFrame:

    df = df.copy()
    
    cols = df.columns.to_list()
    
    for col in cols:  
        if any(p in col for p in lag_vars):
            for lag in lags:
                df[f"{col}_{lag}"] = df[col].shift(lag)
    
    return df


def add_sum_features(
    df: pd.DataFrame,
    sum_vars: list[str] = ["pr", "discharge"],
    lags: list[int] = [3, 7, 14, 21, 28, 35, 42, 56] # in days
    ) -> pd.DataFrame:
    
    df = df.copy()
    
    cols = df.columns.to_list()
    
    for col in cols:    
        if any(p in col for p in sum_vars):
            for d in lags:
                window = d * 24 * 4
                
                df[f"{col}_sum_{d}d"] = (
                    df[col]
                    .rolling(window, min_periods=1)
                    .sum()
                    )

    return df


def create_features(
    df: pd.DataFrame,
    horizon: int = 1
    ) -> pd.DataFrame:
    
    # --- Date transform ---
    df = add_time_transform(df)
    
    # --- Lag features    
    df = add_lag_features(df)
    
    # --- Summed features ---
    df = add_sum_features(df)

    # --- Create shifted target by 15 min -> Predict horizon ---
    df["target"] = df["discharge"].shift(-horizon)
    df.dropna(inplace=True)

    
    return df


def create_training_features(
    df: pd.DataFrame,
    horizon: int = 1,
) -> pd.DataFrame:
    
    df = create_features(df)
    
    # --- Create shifted target by 15 min -> Predict horizon ---
    df["target"] = df["discharge"].shift(-horizon)
    df.dropna(inplace=True)
    
    return df


def create_inference_features(
    df: pd.DataFrame,
) -> pd.DataFrame:
    
    df = create_features(df)
    
    latest = df.tail(1)
    
    return latest