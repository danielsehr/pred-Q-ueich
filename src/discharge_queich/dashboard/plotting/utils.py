import pandas as pd


def add_empty_bars(
    df: pd.DataFrame | pd.Series,
    epsilon: float = 0.001,
    ) -> pd.DataFrame | pd.Series:
    
    plot_vals = df.mask(df == 0, epsilon)
    
    return plot_vals