import pandas as pd

def prepare_df(
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


def prepare_datasets(
    data: dict,
    days: int = 14
    ):
    
    datasets = {
        "discharge": pd.DataFrame(data["discharge"]),
        "inference": pd.DataFrame(data["inference"]),
        "precip_obs": pd.DataFrame(data["precip_obs"]),
        "precip_pred": pd.DataFrame(data["precip_pred"]),
    }
    
    return {
        name: prepare_df(df=df, days=days)
        for name, df in datasets.items()
    }