from dataclasses import dataclass
import pandas as pd

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session

from discharge_queich.configs import settings
from discharge_queich.utils.logger import logger

from discharge_queich.database.db import SessionLocal
from discharge_queich.database.models import IconPrecipForecast

from discharge_queich.jobs.icon.process import build_precip_timeseries
from discharge_queich.jobs.icon.decompress import decompress_bz2_dir
from discharge_queich.jobs.icon.fetch import fetch_icon


icon_settings = settings.ingestion.icon
catchment_settings = settings.ingestion.catchment


def get_latest_timestamp() -> pd.Timestamp | None:
    
    with SessionLocal() as session:
        try:
            stmt = (
                select(IconPrecipForecast.timestamp)
                .order_by(IconPrecipForecast.timestamp.desc())
                .limit(1)
            )
            
            latest = session.scalar(statement=stmt)
            
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
                logger.info("[ICON PRECIP FORECAST] No new data.")
                return IngestionResult()
            
            
            records = (
                df.reset_index()
                .rename(columns={"index": "timestamp"})
                .to_dict(orient="records")
            )
            
            
            stmt = insert(IconPrecipForecast).values(records)
            
            stmt = stmt.on_conflict_do_update(
                index_elements=[IconPrecipForecast.timestamp],
                set_= {
                    IconPrecipForecast.timestamp: stmt.excluded.precip_mean
                }
            )
            
            session.execute(stmt)
            session.commit()
            
            logger.info("[ICON PRECIP FORECAST] Inserted %s rows.", len(records))
            
            return IngestionResult(inserted=len(records))
        
            
        except Exception:
            session.rollback()
            logger.exception("[ICON PRECIP FORECAST] Failed DB ingestion.")
            raise
        
        

def ingest_icon() -> IngestionResult:
    fetch_icon()
    
    decompress_bz2_dir(
        input_dir=icon_settings.compressed_dir,
        output_dir=icon_settings.decompressed_dir
    )
    
    df_precip_mean = build_precip_timeseries(
        input_dir=icon_settings.decompressed_dir,
        catchment_path=catchment_settings.catchment_path,
        clip_crs=icon_settings.clip_crs
    )
    
    latest_ts = get_latest_timestamp()
    df_precip_mean = df_precip_mean[df_precip_mean.index > latest_ts]
    
    ingestion_result = write_to_db(df=df_precip_mean)
    
    return ingestion_result