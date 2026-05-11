from sqlalchemy import Column, Float, DateTime
from database.db import Base


# Create a DB tables
class Discharge(Base):
    __tablename__ = "discharge"

    timestamp = Column(DateTime, primary_key=True)

    discharge = Column(Float, nullable=False)

class Forecast(Base):
    __tablename__ = "forecast"

    timestamp = Column(DateTime, primary_key=True)

    predicted = Column(Float, nullable=False)