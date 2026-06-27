import pandas as pd

from sqlalchemy import select
from sqlalchemy.orm import Session

from discharge_queich.configs import settings
from discharge_queich.utils.logger import logger

from sqlalchemy.exc import SQLAlchemyError

from discharge_queich.database.db import SessionLocal
from discharge_queich.database.models import TempStationObservation
from discharge_queich.jobs.temp.fetch_temp import fetch_temp
from discharge_queich.jobs.temp.process_temp import build_mean_temp_timeseries


temp_settings = settings.ingestion.temp


def get_latest_timestamp() -> pd.Timestamp | None:
    with SessionLocal() as session:
    
        try:
            statement = (
                select(TempStationObservation.timestamp)
                .order_by(TempStationObservation.timestamp.desc())
                .limit(1)
            )
            
            latest = session.scalar(statement=statement)
            
            return pd.Timestamp(latest) if latest is not None else None

        
        except SQLAlchemyError as e:
            logger.exception("Failed query latest timestamp")
            raise
        


def write_to_db(df: pd.DataFrame) -> None:
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
        


def main() -> None: 
    fetch_temp()
    
    latest_ts = get_latest_timestamp()
    
    df_temp_mean = build_mean_temp_timeseries(
        compressed_dir=temp_settings.compressed_dir,
        start=latest_ts
    )
    
    write_to_db(df_temp_mean)
    
    
if __name__ == "__main__":
    main()