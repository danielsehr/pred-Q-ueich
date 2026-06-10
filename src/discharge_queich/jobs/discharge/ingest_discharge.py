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


def write_to_db(df) -> bool:
    session: Session = SessionLocal()

    try:
        last_timestamp = get_last_timestamp(session)
        
        if last_timestamp is not None:
            df = df[df.index > last_timestamp]
        
        if df.empty:
            logger.info("No new data.")
            
            return False


        entries = [
            Discharge(
                timestamp=timestamp,
                discharge=row["discharge"],
            )
            for timestamp, row in df.iterrows()
        ]

        session.add_all(entries)
        session.commit()
        
        logger.info("[DISCHARGE] Inserted %s rows.", len(df))

        return True
        
        
    except Exception:
        session.rollback()
        logger.exception("[DISCHARGE] Failed DB ingestion.")
        return False


    finally:
        session.close()



def main() -> bool:
    df = fetch_discharge()
    
    inserted = write_to_db(df)
    
    return inserted


if __name__ == "__main__":
    main()