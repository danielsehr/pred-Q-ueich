import pandas as pd

from sqlalchemy import select
from sqlalchemy.orm import Session
from database.db import SessionLocal
from database.models import RadolanPrecipObservation

from configs import settings
from utils.logger import logger
from jobs.radolan.fetch_radolan import fetch_radolan
from jobs.radolan.decompress_radolan import decompress_tar_dir
from jobs.radolan.process_radolan import build_precip_timeseries


radolan_settings = settings.ingestion.radolan


def get_latest_timestamp() -> pd.Timestamp | None:
    session = SessionLocal()
    
    try:
        statement = (
            select(RadolanPrecipObservation.timestamp)
            .order_by(RadolanPrecipObservation.timestamp.desc())
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
            
            entry = RadolanPrecipObservation(
                timestamp=timestamp,
                precip_mean=row["precip_mean"]
            )
            
            session.merge(entry)
            
        session.commit()
        
        logger.info("[RADOLAN PRECIP OBSERV] Inserted %s rows.", len(df))

    
    except Exception:
        session.rollback()
        logger.exception("[RADOLAN PRECIP OBSERV] Failed DB ingestion.")
        raise
    
    
    finally:
        session.close()
        


def main() -> None: 
    fetch_radolan()
    
    decompress_tar_dir(
        input_dir=radolan_settings.compressed_dir,
        output_dir=radolan_settings.decompressed_dir,
        days=30
    )
    
    latest_ts = get_latest_timestamp()
    
    df_precip_mean = build_precip_timeseries(
        input_dir=radolan_settings.decompressed_dir,
        catchment_path=settings.ingestion.catchment.catchment_path,
        start=latest_ts
    )
    
    write_to_db(df_precip_mean)
    
    
if __name__ == "__main__":
    main()
    
    
    
    