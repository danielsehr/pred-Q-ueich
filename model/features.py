import numpy as np
import pandas as pd


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    
    # --- Date transform ---
    df.index = pd.to_datetime(df.index)

    # Add sin cos date transform to data
    df["doy_sin"] = np.sin(2*np.pi * df.index.dayofyear / 365)
    df["doy_cos"] = np.cos(2*np.pi * df.index.dayofyear / 365)
    
    
    # --- Lag features    
    lag_vars = ["pr", "temp", "pet", "discharge"]
    lags = [1, 2, 4, 8, 12, 24, 48, 96]

    for col in df.columns:
        if any(p in col for p in lag_vars):
            for lag in lags:
                df[f"{col}_{lag}"] = df[col].shift(lag)
    
    
    # --- Summed features ---
    sum_vars = ["pr", "discharge"]
    days = [3, 7, 14, 21, 28, 35, 42, 56]
    
    for col in df.columns:    
        if any(p in col for p in sum_vars):
            for d in days:
                window = d * 24 * 4
                
                df[f"{col}_sum_{d}"] = (
                    df[col]
                    .rolling(window, min_periods=1)
                    .sum()
                    )


    # --- Predict 4*15 min = 1h ahead
    df["target"] = df["discharge"].shift(-4)

    df.dropna(inplace=True)
    
    
    return df