from pathlib import Path
import pandas as pd
from xgboost import XGBRegressor

from configs import settings


def load_model():
    model = XGBRegressor()
    model.load_model(fname=settings.model.inference.model_path)
    
    return model


def run_inference(df: pd.DataFrame):
    model = load_model()
    
    return model.predict(df)