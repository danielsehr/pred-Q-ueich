from pathlib import Path
import pandas as pd

from discharge_queich.configs import settings


temp_settings = settings.ingestion.temp_recent


def read_temp_zip(
    zip_path: str | Path
    ) -> pd.DataFrame:

    df = pd.read_csv(
        zip_path,
        sep=";",
        compression="zip"
        )

    return df


def build_temp_timeseries(
    df: pd.DataFrame,
    cols_to_keep: list[str],
    cols_rename: list[str],
    ) -> pd.DataFrame:
    
    df = df.copy()
    
    # Subset and rename
    df = df[cols_to_keep]
    df.columns = cols_rename
    
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y%m%d%H%M")
    
    df = df.set_index(keys="timestamp")
    df = df.sort_index()
    
    df = df.mask(df < -50)
    
    return df

    
def resample_temp(df: pd.DataFrame) -> pd.DataFrame:
    
    df_10min = df.copy()

    df_15min = (
        df_10min.resample("15min")
                .interpolate(method="time")
        )
    
    return df_15min


def build_mean_temp_timeseries(
    compressed_dir: str | Path = temp_settings.compressed_dir,
    start: pd.Timestamp | None = None
    ) -> pd.DataFrame:
    
    zip_files = [p for p in Path(compressed_dir).rglob("*.zip")]
    
    dfs = {}
    
    for file in zip_files:
        
        file_name = Path(file).stem
                
                
        df = read_temp_zip(zip_path=file)

        df = build_temp_timeseries(
            df=df,
            cols_to_keep=temp_settings.cols_to_keep,
            cols_rename=temp_settings.cols_rename,
            )

        df = resample_temp(df=df)
        
        
        dfs[file_name] = df
        
        
    df = pd.concat(
        [df["temp"] for df in dfs.values()],
        axis=1
        ).mean(axis=1).to_frame("temp_mean")

    df = (
            df
            .mean(axis=1)
            .to_frame("temp_mean")
        )
    
    if start is not None:
        df = df[df.index >= start]

        
    return df