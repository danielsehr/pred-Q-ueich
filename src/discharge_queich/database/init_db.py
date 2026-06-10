from discharge_queich.database.db import engine
from discharge_queich.database.models import Base


def initiate_database():
    Base.metadata.create_all(bind=engine)

    print("Database initialized.")
    print(Base.metadata.tables.keys())