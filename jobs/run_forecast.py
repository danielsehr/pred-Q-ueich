from datetime import datetime
import random

from database.db import SessionLocal
from database.models import Forecast


session = SessionLocal()


entry = Forecast(
    timestamp = datetime.utcnow(),
    observed = random.uniform(1.0, 5.0),
    predicted = random.uniform(1.0, 5.0)
)

session.add(entry)
session.commit()

print("Forecast inserted.")