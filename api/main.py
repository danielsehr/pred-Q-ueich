from fastapi import FastAPI

from database.db import SessionLocal 
from database.models import Forecast

app = FastAPI()

@app.get("/forecast")

def get_forecast():
    session = SessionLocal()
    
    rows = session.query(Forecast).all()
    
    return [
        {
            "timestamp": r.timestamp,
            "observed": r.observed,
            "predicted": r.predicted,
        }
        for r in rows
    ]