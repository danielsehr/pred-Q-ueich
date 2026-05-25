from fastapi import FastAPI

from database.db import SessionLocal 
from database.models import Discharge, Inference
from database.queries import load_discharge_data, load_inference_data, load_precip_observation_data, load_precip_forecast_data


# Create web application instance -> main backend server object
app = FastAPI()

# Decorator -> when sb. GET requests to /forecast -> run function:
# When streamlit do requests.get() -> get_forecast() is executed.
@app.get("/forecast")

def get_forecast():
    df_discharge = load_discharge_data()
    df_inference = load_inference_data()
    df_precip_obs = load_precip_observation_data()
    df_precip_pred = load_precip_forecast_data()
    
    return {
        "discharge": df_discharge.reset_index().to_dict(orient="records"),
        "inference": df_inference.reset_index().to_dict(orient="records"),
        "precip_obs": df_precip_obs.reset_index().to_dict(orient="records"),
        "precip_pred": df_precip_pred.reset_index().to_dict(orient="records"),
    }
        