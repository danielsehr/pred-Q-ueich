from sqlalchemy import Column, Float, DateTime
from database.db import Base

class Forecast(Base):
    __tablename__ = "forecast"

    timestamp = Column(DateTime, primary_key=True)

    observed = Column(Float)

    predicted = Column(Float)