import numpy as np
import pandas as pd

from discharge_queich.configs import settings


feature_settings = settings.model.features


def add_time_transform(df: pd.DataFrame) -> pd.DataFrame:
    
    DAYS_PER_YEAR = 365
    HOURS_PER_DAY = 24
    MINUTES_PER_HOUR = 60
    
    df = df.copy()
    
    df.index = pd.to_datetime(df.index)

    # Day of year transform
    df["doy_sin"] = np.sin(2 * np.pi * df.index.dayofyear / DAYS_PER_YEAR)
    df["doy_cos"] = np.cos(2 * np.pi * df.index.dayofyear / DAYS_PER_YEAR)
    
    # Minute of day transform
    minutes_of_day = (df.index.hour * MINUTES_PER_HOUR + df.index.minute)
    df["mod_sin"] = np.sin(2 * np.pi * minutes_of_day / (HOURS_PER_DAY * MINUTES_PER_HOUR))
    df["mod_cos"] = np.cos(2 * np.pi * minutes_of_day / (HOURS_PER_DAY * MINUTES_PER_HOUR))

    return df


def add_shift_features(
    df: pd.DataFrame, 
    cols: list[str],
    lag_vars: list[str],
    lags: list[int]
    ) -> pd.DataFrame:

    df = df.copy()
    
    for col in cols:  
        if any(p in col for p in lag_vars):
            for lag in lags:
                df[f"{col}_{lag}"] = df[col].shift(lag)
    
    return df


def add_sum_features(
    df: pd.DataFrame,
    cols: list[str],
    sum_vars: list[str],
    lags: list[int]
    ) -> pd.DataFrame:
    
    df = df.copy()
    
    new_cols = {}
    
    for col in cols:    
        if any(p in col for p in sum_vars):
            for delay in feature_settings.delays:
                for window in feature_settings.sum_lags:
                
                    new_cols[f"{col}_delay_{delay}_sum_{window}"] = (
                        df[col]
                        .shift(delay)
                        .rolling(window, min_periods=1)
                        .sum()
                        )

    df = pd.concat(
        [df, pd.DataFrame(new_cols, index=df.index)], 
        axis=1
        )
    
    return df


def create_features(
    df: pd.DataFrame
    ) -> pd.DataFrame:
    
    # Define columns
    cols = df.columns.to_list()
    
    # --- Date transform ---
    df = add_time_transform(df)
    
    # --- Shift lag features    
    df = add_shift_features(df, cols=cols, lags=feature_settings.shift_lags, lag_vars=feature_settings.shift_vars)
    
    # --- Summed lag features ---
    df = add_sum_features(df, cols=cols, lags=feature_settings.sum_lags, sum_vars=feature_settings.sum_vars)
    
    return df


def create_training_features(
    df: pd.DataFrame,
    horizon: int = settings.model.inference.steps,
    ) -> pd.DataFrame:
    
    df = df.copy()
    df = create_features(df)
    
    # --- Create shifted target by 15 min -> Predict horizon ---
    # df["target"] = df["discharge"].shift(-horizon)
    df["target"] = df["discharge"].shift(-horizon) - df["discharge"]
    df.dropna(inplace=True)
    
    return df


def create_inference_features(
    df: pd.DataFrame,
    ) -> pd.DataFrame:
    
    df = df.copy()
    df = create_features(df)
    
    latest = df.tail(1)
    
    return latest