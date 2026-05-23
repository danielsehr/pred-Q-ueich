from sqlalchemy.orm import Session

from database.db import SessionLocal
from database.models import Discharge

from utils.logger import logger
from jobs.fetch_discharge import fetch_discharge


def get_last_timestamp(session: Session):
    result = (
        session.query(Discharge.timestamp)
        .order_by(Discharge.timestamp.desc())
        .first()
    )
    return result[0] if result else None


def write_to_db(df):
    session: Session = SessionLocal()

    try:
        last_timestamp = get_last_timestamp(session)
        
        if last_timestamp is not None:
            df = df[df.index > last_timestamp]
        
        if df.empty:
            logger.info("No new data.")
            return

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


    except Exception:
        session.rollback()
        logger.exception("[DISCHARGE] Failed DB ingestion.")
        return


    finally:
        session.close()



def main() -> None:
    df = fetch_discharge()
    
    write_to_db(df)


if __name__ == "__main__":
    main()