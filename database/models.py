from sqlalchemy import Column, Float, String, DateTime
from database.db import Base


# Create a DB tables
class Discharge(Base):
    __tablename__ = "discharge"

    timestamp = Column(DateTime, primary_key=True)

    discharge = Column(Float, nullable=False)


class Inference(Base):
    __tablename__ = "inference"

    timestamp = Column(DateTime, primary_key=True)

    observed = Column(Float, nullable=False)
    
    predicted = Column(Float)
    
    model_version = Column(String)