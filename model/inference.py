from pathlib import Path
import pandas as pd
from xgboost import XGBRegressor


MODEL_PATH = Path("models/xgb_model.json")


def load_model():
    model = XGBRegressor()
    model.load_model(MODEL_PATH)
    
    return model


def run_inference(df: pd.DataFrame):
    model = load_model()
    
    return model.predict(df)