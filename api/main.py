from fastapi import FastAPI

from database.db import SessionLocal 
from database.models import Discharge, Forecast


# Create web application instance -> main backend server object
app = FastAPI()

# Decorator -> when sb. GET requests to /forecast -> run function:
# When streamlit do requests.get() -> get_forecast() is executed.
@app.get("/forecast")

def get_forecast():
    # Create live DB session / connection
    session = SessionLocal()
    
    # Query forecast table in SQL for all rows -> SELECT * FROM forecast
    rows = session.query(Discharge).all()
    
    # Return row objects in list of dicts, FastAPI directly dumps it into json http response
    return [
        {
            "timestamp": r.timestamp.isoformat(),
            "discharge": r.discharge,
        }
        for r in rows
    ]