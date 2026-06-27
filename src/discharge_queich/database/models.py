from sqlalchemy import Column, Float, String, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from pandas import Timestamp
from datetime import datetime

from discharge_queich.database.db import Base


class Discharge(Base):
    __tablename__ = "discharge"

    timestamp: Mapped[datetime] = mapped_column(DateTime, primary_key=True)

    discharge: Mapped[float] = mapped_column(Float)



class Inference(Base):
    __tablename__ = "inference"

    timestamp: Mapped[datetime] = mapped_column(DateTime, primary_key=True)

    predicted: Mapped[float] = mapped_column(Float)
    
    # model_version = Column(String)
    


class IconPrecipForecast(Base):
    __tablename__ = "icon_precip_mean_forecast"
        
    timestamp: Mapped[datetime] = mapped_column(DateTime, primary_key=True)
    
    precip_mean: Mapped[float] = mapped_column(Float)



class RadolanPrecipObservation(Base):
    __tablename__ = "radolan_precip_mean_observation"
    
    timestamp: Mapped[datetime] = mapped_column(DateTime, primary_key=True)
    
    precip_mean: Mapped[float] = mapped_column(Float)



class RadolanPrecipHourlyObservation(Base):
    __tablename__ = "radolan_precip_hourly_mean_observation"
    
    timestamp: Mapped[datetime] = mapped_column(DateTime, primary_key=True)
    
    precip_mean: Mapped[float] = mapped_column(Float)
    
    

class TempStationFileState(Base):
    __tablename__ = "temp_station_file_state"
    
    __table_args__ = (
        UniqueConstraint(
            "station_id",
            "timestamp",
            "etag",
            name="uq_temp_station_file_state",
        ),
    )
    
    station_id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        nullable=False
        )
    
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
        )
    
    etag: Mapped[str] = mapped_column(String)
    
    last_modified: Mapped[datetime] = mapped_column(DateTime)