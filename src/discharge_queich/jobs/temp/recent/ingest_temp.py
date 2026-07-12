import pandas as pd

from discharge_queich.configs import settings
from discharge_queich.utils.logger import logger

from discharge_queich.database.db import SessionLocal
from discharge_queich.database.models import TempStationObservation
from discharge_queich.jobs.temp.recent.fetch_temp import fetch_temp
from discharge_queich.jobs.temp.recent.process_temp import build_mean_temp_timeseries 

temp_settings = settings.ingestion.temp_recent


def write_to_db(df: pd.DataFrame | pd.Series) -> None:
    with SessionLocal() as session:
    
        try:
            for timestamp, row in df.iterrows():
                
                entry = TempStationObservation(
                    timestamp=timestamp,
                    temp_mean=row["temp_mean"]
                )
                
                session.merge(entry)
                
            session.commit()
            
            logger.info("[STATIONS TEMP OBSERV] Inserted %s rows.", len(df))

        
        except Exception:
            session.rollback()
            logger.exception("[STATIONS TEMP OBSERV] Failed DB ingestion.")
            raise
        

def subset_timeseries(df: pd.DataFrame) -> pd.Series:
    
    latest = df.index.max()
    cutoff = latest - pd.DateOffset(months=1)

    return df[df.index >= cutoff]



def main() -> None:
    fetch_temp()
    
    df_temp_mean = build_mean_temp_timeseries(
        compressed_dir=temp_settings.compressed_dir,
        start=None
    )

    df_temp_mean = subset_timeseries(df=df_temp_mean)
    
    write_to_db(df=df_temp_mean)
    
    