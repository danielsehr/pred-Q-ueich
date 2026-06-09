from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = BASE_DIR / "queich.db"

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


# Database driver / connection manager -> communcation interface to the DB
# "connect python to SQLite"
engine = create_engine(DATABASE_URL)

# Create session with engine
SessionLocal = sessionmaker(bind=engine)

# Base class for all DB models -> master blueprint for tables
Base = declarative_base()