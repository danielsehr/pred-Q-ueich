from src.database.db import engine
from src.database.models import Base

# Build the database from engine and blueprint class
Base.metadata.create_all(bind=engine)

print("Database initialized.")
print(Base.metadata.tables.keys())