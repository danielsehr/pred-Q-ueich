import pandas as pd

from sqlalchemy import select
from sqlalchemy.orm import Session
from database.db import SessionLocal
from database.models import IconPrecipForecast

from configs import settings
from utils.logger import logger

from jobs.icon.process_icon import build_precip_timeseries
from jobs.icon.decompress_icon import decompress_bz2_dir
from jobs.icon.fetch_icon import fetch_icon


icon_settings = settings.ingestion.icon
catchment_settings = settings.ingestion.catchment


def get_latest_timestamp() -> pd.Timestamp | None:
    session = SessionLocal()
    
    try:
        statement = (
            select(IconPrecipForecast.timestamp)
            .order_by(IconPrecipForecast.timestamp.desc())
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
            
            entry = IconPrecipForecast(
                timestamp=timestamp,
                precip_mean=row["precip_mean"]
            )
            
            session.merge(entry)
        
        session.commit()
        
        logger.info("[ICON PRECIP FORECAST] Inserted %s rows.", len(df))
        
        
    except Exception:
        session.rollback()
        logger.exception("[ICON PRECIP FORECAST] Failed DB ingestion.")
        raise
    
    
    finally:
        session.close()
        
        

def main() -> None:
    fetch_icon()
    
    decompress_bz2_dir(
        input_dir=icon_settings.compressed_dir,
        output_dir=icon_settings.compressed_dir
    )
    
    df_precip_mean = build_precip_timeseries(
        input_dir=icon_settings.compressed_dir,
        catchment_path=catchment_settings.catchment_path,
        clip_crs=icon_settings.clip_crs
    )
    
    latest_ts = get_latest_timestamp()
    df_precip_mean = df_precip_mean[df_precip_mean.index > latest_ts]
    
    write_to_db(df_precip_mean)
    
    
if __name__ == "__main__":
    main()