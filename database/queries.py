import pandas as pd

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from utils.logger import logger
from database.db import SessionLocal
from database.models import Discharge, Inference


def load_discharge_data() -> pd.DataFrame:
    session = SessionLocal()
    
    try:
        statement = (
            select(Discharge)
            .order_by(Discharge.timestamp)
        )
        
        rows = session.execute(statement=statement).scalars().all()
        
        df = pd.DataFrame(
            [
                {
                    "timestamp": r.timestamp,
                    "discharge": r.discharge, 
                }
                for r in rows
            ]
        )
        
        if not df.empty:
            df = df.set_index(keys="timestamp")
            
        return df
    
    except SQLAlchemyError:
        logger.exception("Failed to load discharge data")
        raise
    
    
    finally:
        session.close()
        


def load_inference_data() -> pd.DataFrame:
    session = SessionLocal()
    
    try:
        statement = (
            select(Inference)
            .order_by(Inference.timestamp)
        )
        
        rows = session.execute(statement=statement).scalars().all()
        
        df = pd.DataFrame(
            [
                {
                    "timestamp": r.timestamp,
                    "predicted": r.predicted,
                    # "model_version": r.model_version
                }
                for r in rows
            ]
        )
        
        if not df.empty:
            df = df.set_index(keys="timestamp")
        
        return df
    
    
    except SQLAlchemyError:
        logger.exception("Failed to load inference data")
        raise
    
    
    finally:
        session.close()