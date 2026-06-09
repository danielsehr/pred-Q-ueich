import pandas as pd

from sqlalchemy import select
from sqlalchemy.orm import Session
from src.database.db import SessionLocal
from src.database.models import RadolanPrecipHourlyObservation

from configs import settings
from src.utils.logger import logger
from src.jobs.radolan_hourly.fetch_radolan import fetch_radolan
from src.jobs.radolan_hourly.process_radolan import build_precip_timeseries


radolan_settings = settings.ingestion.radolan_hourly


def get_latest_timestamp() -> pd.Timestamp | None:
    session = SessionLocal()
    
    try:
        statement = (
            select(RadolanPrecipHourlyObservation.timestamp)
            .order_by(RadolanPrecipHourlyObservation.timestamp.desc())
            .limit(1)
        )
        
        latest = session.scalar(statement=statement)
        
        return pd.Timestamp(latest) if latest is not None else None
    
    
    finally:
        session.close()
        


def write_to_db(df: pd.DataFrame) -> None:
    session: Session = SessionLocal()
    
    try:
        for timestamp, row in df.iterrows():
            
            entry = RadolanPrecipHourlyObservation(
                timestamp=timestamp,
                precip_mean=row["precip_mean"]
            )
            
            session.merge(entry)
            
        session.commit()
        
        logger.info("[RADOLAN PRECIP HOURLY OBSERV] Inserted %s rows.", len(df))

    
    except Exception:
        session.rollback()
        logger.exception("[RADOLAN PRECIP HOURLY OBSERV] Failed DB ingestion.")
        raise
    
    
    finally:
        session.close()
        


def main() -> None: 
    fetch_radolan()
    
    latest_ts = get_latest_timestamp()
    
    df_precip_mean = build_precip_timeseries(
        input_dir=radolan_settings.compressed_dir,
        catchment_path=settings.ingestion.catchment.catchment_path,
        start=latest_ts
    )
    
    write_to_db(df_precip_mean)
    
    
if __name__ == "__main__":
    main()