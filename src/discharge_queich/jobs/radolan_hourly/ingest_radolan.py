from dataclasses import dataclass
import pandas as pd

from sqlalchemy.dialects.sqlite import insert
from sqlalchemy import select
from sqlalchemy.orm import Session

from discharge_queich.configs import settings
from discharge_queich.utils.logger import logger

from discharge_queich.database.db import SessionLocal
from discharge_queich.database.models import RadolanPrecipHourlyObservation

from discharge_queich.jobs.radolan_hourly.fetch_radolan import fetch_radolan
from discharge_queich.jobs.radolan_hourly.process_radolan import build_precip_timeseries


radolan_settings = settings.ingestion.radolan_hourly


def get_latest_timestamp() -> pd.Timestamp | None:
    with SessionLocal() as session:
    
        try:
            statement = (
                select(RadolanPrecipHourlyObservation.timestamp)
                .order_by(RadolanPrecipHourlyObservation.timestamp.desc())
                .limit(1)
            )
            
            latest = session.scalar(statement=statement)
            
            return pd.Timestamp(latest) if latest is not None else None


        except Exception:
            session.rollback()
            raise


@dataclass
class IngestionResult:
    inserted: int = 0

    @property
    def changed(self) -> bool:
        return self.inserted > 0
    

def write_to_db(df: pd.DataFrame) -> IngestionResult:
    with SessionLocal() as session:
    
        try:
            if df.empty:
                logger.info("[RADOLAN PRECIP HOURLY OBSERV] No new data.")
                return IngestionResult()
                
            
            records = (
                df.reset_index()
                .rename(columns={"index": "timestamp"})
                .to_dict(orient="records")
            )

            stmt = insert(RadolanPrecipHourlyObservation).values(records)
            
            stmt = stmt.on_conflict_do_update(
                index_elements=[RadolanPrecipHourlyObservation.timestamp],
                set_ = {
                    RadolanPrecipHourlyObservation.timestamp: stmt.excluded.precip_mean
                }
            )
                
            session.execute(stmt)
            session.commit()
            
            logger.info("[RADOLAN PRECIP HOURLY OBSERV] Inserted %s rows.", len(records))

            return IngestionResult(inserted=len(records))
    
    
        except Exception:
            session.rollback()
            logger.exception("[RADOLAN PRECIP HOURLY OBSERV] Failed DB ingestion.")
            raise


def ingest_radolan() -> IngestionResult: 
    fetch_radolan()
    
    latest_ts = get_latest_timestamp()
    
    df_precip_mean = build_precip_timeseries(
        input_dir=radolan_settings.compressed_dir,
        catchment_path=settings.ingestion.catchment.catchment_path,
        start=latest_ts
    )
    
    ingestion_result = write_to_db(df_precip_mean)
    
    return ingestion_result