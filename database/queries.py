import pandas as pd

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from configs.database_config import QUERY_TIMEDELTA_DAYS
from utils.logger import logger
from database.db import SessionLocal
from database.models import Discharge, Inference, IconPrecipForecast, RadolanPrecipObservation




def load_timeseries(
    model,
    value_column: str,
    output_name: str,
    days: int,
    ) -> pd.DataFrame:
    
    end = pd.Timestamp.now()
    start = end - pd.Timedelta(days=days)

    
    column = getattr(model, value_column)
    
    with SessionLocal() as session:
        statement = (
            select(model.timestamp, column)
            .where(model.timestamp > start)
            .where(model.timestamp <= end)
            .order_by(model.timestamp)
        )

        rows = session.execute(statement).all()
        
        
    df = pd.DataFrame(
        [
            {
                "timestamp": ts,
                output_name: value
            } for ts, value in rows
        ] 
    )
    
    if not df.empty:
        df = df.set_index("timestamp")
        
    return df

    

def load_discharge_data(
    days: int = QUERY_TIMEDELTA_DAYS
    ) -> pd.DataFrame:
    
    df = load_timeseries(
        model=Discharge, 
        value_column="discharge",
        output_name="discharge",
        days=days
    )
    
    return df


def load_inference_data(
    days: int = QUERY_TIMEDELTA_DAYS
    ) -> pd.DataFrame:
    
    df = load_timeseries(
        model=Inference, 
        value_column="predicted",
        output_name="predicted",
        days=days
    )
    
    return df
    

def load_precip_forecast_data(
    days: int = QUERY_TIMEDELTA_DAYS
    ) -> pd.DataFrame:
    
    df = load_timeseries(
        model=IconPrecipForecast, 
        value_column="precip_mean",
        output_name="precip_mean",
        days=days
    )
    
    return df
        

def load_precip_observation_data(
    days: int = QUERY_TIMEDELTA_DAYS
    ) -> pd.DataFrame:
    
    df = load_timeseries(
        model=RadolanPrecipObservation, 
        value_column="precip_mean",
        output_name="precip_mean",
        days=days
    )
    
    return df