import pandas as pd

def prepare_data(
    df: pd.DataFrame,
    days: int
    ) -> pd.DataFrame:
    
    # --- Datetime ---
    df = df.set_index(keys=["timestamp"])
    df.index = pd.to_datetime(df.index)
    
    # --- Set cutoff ---
    latest = df.index.max()
    cutoff = latest -  pd.Timedelta(days=days)
    
    df = df[df.index >= cutoff]
    
    return df