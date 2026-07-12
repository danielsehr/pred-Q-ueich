from dataclasses import dataclass
import pandas as pd

from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session

from discharge_queich.database.db import SessionLocal
from discharge_queich.database.models import Discharge

from discharge_queich.utils.logger import logger
from discharge_queich.jobs.discharge.fetch_discharge import fetch_discharge


def get_last_timestamp(session: Session):
    result = (
        session.query(Discharge.timestamp)
        .order_by(Discharge.timestamp.desc())
        .first()
    )
    return result[0] if result else None


@dataclass
class IngestionResult:
    inserted: int = 0

    @property
    def changed(self) -> bool:
        return self.inserted > 0
            

def write_to_db(df: pd.DataFrame | pd.Series) -> IngestionResult:

    with SessionLocal() as session:
        try:
            last_timestamp = get_last_timestamp(session)
            
            if last_timestamp is not None:
                df = df[df.index > last_timestamp]
            
            if df.empty:
                logger.info("[DISCHARGE] No new data.")
                return IngestionResult()

            
            records = (
                df.reset_index()
                .rename(columns={"index": "timestamp"})
                .to_dict(orient="records")
            )
            
            
            stmt = insert(Discharge).values(records)
            
            stmt = stmt.on_conflict_do_update(
                index_elements=[Discharge.timestamp],
                set_= {
                    Discharge.timestamp: stmt.excluded.discharge
                }
            )
            
            session.execute(stmt)
            session.commit()
        
            logger.info("[DISCHARGE] Inserted %s rows.", len(records))

            return IngestionResult(inserted=len(records))
        
        
        except Exception:
            session.rollback()
            logger.exception("[DISCHARGE] Failed DB ingestion.")
            raise

        

def ingest_discharge() -> IngestionResult:
    df = fetch_discharge()
    
    ingestion_result = write_to_db(df)
    
    return ingestion_result