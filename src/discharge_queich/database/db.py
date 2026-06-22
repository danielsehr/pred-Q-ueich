from pathlib import Path

from discharge_queich.configs import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# Create engine
engine = create_engine(url=settings.database.database_url)

# Create session
SessionLocal = sessionmaker(bind=engine)

# Base class for all DB models -> master blueprint for tables
Base = declarative_base()