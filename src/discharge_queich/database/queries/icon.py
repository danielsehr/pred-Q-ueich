from dataclasses import dataclass
import pandas as pd

from sqlalchemy import select, func
from sqlalchemy.dialects.sqlite import insert

from discharge_queich.utils.logger import logger

from discharge_queich.database.db import SessionLocal
from discharge_queich.database.models import IconPrecipForecastAllruns


def get_latest_runtime() -> pd.Timestamp | None:
    stmt = (
        select(
            func.max(IconPrecipForecastAllruns.run_time)
            )
        )
    
    with SessionLocal() as session:
        
        latest = session.execute(stmt).scalar()
        
        if latest is None:
            return None

        return pd.Timestamp(latest)
    

@dataclass
class IngestionResult:
    inserted: int = 0

    @property
    def changed(self) -> bool:
        return self.inserted > 0
    
    def __iadd__(self, other: "IngestionResult"):
        self.inserted += other.inserted
        return self


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
            
            
            stmt = insert(IconPrecipForecastAllruns).values(records)
            
            stmt = stmt.on_conflict_do_update(
                index_elements=[
                    IconPrecipForecastAllruns.run_time,
                    IconPrecipForecastAllruns.timestamp
                    ],
                set_= {
                    IconPrecipForecastAllruns.precip_mean: stmt.excluded.precip_mean
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