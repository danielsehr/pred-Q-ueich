import pandas as pd


def prepare_observation_df(
    df: pd.DataFrame,
    days: int
    ) -> pd.DataFrame:
    
    # --- Datetime ---
    df = df.set_index(keys=["timestamp"])
    df.index = pd.to_datetime(df.index)
    
    # --- Set cutoff ---
    latest = df.index.max()
    cutoff = latest - pd.Timedelta(days=days)
    
    df = df[df.index >= cutoff]
    
    return df


def prepare_forecast_df(
    df: pd.DataFrame,
    # days: int,
    ) -> pd.DataFrame:
    
    # --- Datetime ---
    df = df.set_index(keys=["timestamp"])
    df.index = pd.to_datetime(df.index)
    
    return df


def prepare_datasets(
    data: dict,
    days: int = 14
    ):
    
    discharge = pd.DataFrame(data["discharge"])
    inference = pd.DataFrame(data["inference"])
    precip_obs = pd.DataFrame(data["precip_obs"])
    precip_hourly_obs = pd.DataFrame(data["precip_hourly_obs"])
    precip_pred = pd.DataFrame(data["precip_pred"])
    
    datasets = {
        "discharge": prepare_observation_df(
            discharge,
            days=days
            ),
        
        "inference": prepare_forecast_df(
            inference,
            ),
        
        "precip_obs": prepare_observation_df(
            precip_obs,
            days=days
            ),
        
        "precip_hourly_obs": prepare_observation_df(
            precip_hourly_obs,
            days=days
            ),
        
        "precip_pred": prepare_forecast_df(
            precip_pred,
            ),
        }
    
    return datasets