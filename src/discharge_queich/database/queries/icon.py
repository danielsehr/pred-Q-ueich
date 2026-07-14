import pandas as pd

from sqlalchemy import select, func
from discharge_queich.database.db import SessionLocal
from discharge_queich.database.models import IconPrecipForecastAllruns



def get_latest_runtime() -> pd.Timestamp | None:
    with SessionLocal() as session:
        
        stmt = (
            func.max(
                select(IconPrecipForecastAllruns.run_time)
                .scalar_subquery()
                )
            )
        
        result = session.execute(stmt)
        
        latest = result.scalar()
        
        if latest is None:
            return None

        return pd.Timestamp(latest)