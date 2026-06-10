from sqlalchemy import Column, Float, String, DateTime, UniqueConstraint

from discharge_queich.database.db import Base


# Create a DB tables
class Discharge(Base):
    __tablename__ = "discharge"

    timestamp = Column(DateTime, primary_key=True)

    discharge = Column(Float, nullable=False)



class Inference(Base):
    __tablename__ = "inference"

    __table_args__ = (
        UniqueConstraint(
            "timestamp",
            # "model_version",
            name="uq_inference_timestamp_model",
        ),
    )

    timestamp = Column(DateTime, primary_key=True)

    predicted = Column(Float)
    
    # model_version = Column(String)
    


class IconPrecipForecast(Base):
    __tablename__ = "icon_precip_mean_forecast"
    
    __table_args__ = (
        UniqueConstraint(
            "timestamp",
            name="uq_icon_precip_mean_forecast_timestamp_model",
        ),
    )
    
    timestamp = Column(DateTime, primary_key=True)
    
    precip_mean = Column(Float)



class RadolanPrecipObservation(Base):
    __tablename__ = "radolan_precip_mean_observation"
    
    __table_args__ = (
        UniqueConstraint(
            "timestamp",
            name="uq_icon_precip_mean_forecast_timestamp_model",
        ),
    )
    
    timestamp = Column(DateTime, primary_key=True)
    
    precip_mean = Column(Float)



class RadolanPrecipHourlyObservation(Base):
    __tablename__ = "radolan_precip_hourly_mean_observation"
    
    __table_args__ = (
        UniqueConstraint(
            "timestamp",
            name="uq_icon_precip_hourly_mean_forecast_timestamp_model",
        ),
    )
    
    timestamp = Column(DateTime, primary_key=True)
    
    precip_mean = Column(Float)