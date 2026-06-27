import pandas as pd

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from discharge_queich.configs import settings

from discharge_queich.utils.logger import logger
from discharge_queich.database.db import SessionLocal

from discharge_queich.database.models import (
    Discharge, Inference, IconPrecipForecast, 
    RadolanPrecipObservation, RadolanPrecipHourlyObservation,
    TempStationObservation
    )


def load_observation_timeseries(
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


def load_forecast_timeseries(
    model,
    value_column: str,
    output_name: str,
    days: int,
    ) -> pd.DataFrame:
    
    start = pd.Timestamp.now() - pd.Timedelta(days=days)
    end = pd.Timestamp.now() + pd.Timedelta(days=days)

    
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
    days: int = settings.database.query_timedelta_days
    ) -> pd.DataFrame:
    
    df = load_observation_timeseries(
        model=Discharge, 
        value_column="discharge",
        output_name="discharge",
        days=days
    )
    
    return df


def load_inference_data(
    days: int = settings.database.query_timedelta_days
    ) -> pd.DataFrame:
    
    df = load_forecast_timeseries(
        model=Inference, 
        value_column="predicted",
        output_name="predicted",
        days=days
    )
    
    return df
    

def load_precip_forecast_data(
    days: int = settings.database.query_timedelta_days
    ) -> pd.DataFrame:
    
    df = load_forecast_timeseries(
        model=IconPrecipForecast, 
        value_column="precip_mean",
        output_name="precip_mean",
        days=days
    )
    
    return df
        

def load_precip_observation_data(
    days: int = settings.database.query_timedelta_days
    ) -> pd.DataFrame:
    
    df = load_observation_timeseries(
        model=RadolanPrecipObservation, 
        value_column="precip_mean",
        output_name="precip_mean",
        days=days
    )
    
    return df


def load_precip_hourly_observation_data(
    days: int = settings.database.query_timedelta_days
    ) -> pd.DataFrame:
    
    df = load_observation_timeseries(
        model=RadolanPrecipHourlyObservation, 
        value_column="precip_mean",
        output_name="precip_mean",
        days=days
    )
    
    return df


def load_temp_observation_data(
    days: int = settings.database.query_timedelta_days
    ) -> pd.DataFrame:
    
    df = load_observation_timeseries(
        model=TempStationObservation,
        value_column="temp_mean",
        output_name="temp_mean",
        days=days
    )
    
    return df