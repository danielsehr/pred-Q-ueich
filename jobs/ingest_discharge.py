from sqlalchemy.orm import Session

from database.db import SessionLocal
from database.models import Discharge

from jobs.fetch_discharge import fetch


def write_to_db(df):
    session: Session = SessionLocal()

    try:
        for timestamp, row in df.iterrows():

            entry = Discharge(
                timestamp=timestamp,
                discharge=row["discharge"],
            )

            session.merge(entry)

        session.commit()

    finally:
        session.close()


if __name__ == "__main__":
    df = fetch()

    write_to_db(df)

    print(f"Inserted {len(df)} rows.")