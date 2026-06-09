from sqlalchemy.orm import Session
import pandas as pd

from src.utils.logger import logger
from src.database.db import SessionLocal
from src.database.models import Inference
from src.database.queries import load_discharge_data, load_precip_observation_data
from src.model.features import create_inference_features
from src.model.inference import run_inference


def write_to_db(df: pd.DataFrame) -> None:
    session: Session = SessionLocal()
    
    try:
        for timestamp, row in df.iterrows():

            entry = Inference(
                timestamp=timestamp,
                predicted=row["predicted"],
                # model_version=row["model_version"],
            )
            
            session.merge(entry)
        
        session.commit()
        
        logger.info("[INFERENCE] Inserted %s rows.", len(df))
         
    
    except Exception:
        session.rollback()
        logger.exception("[INFERENCE] Failed DB ingestion.")
        raise
        
        
    finally:
        session.close()
        
        
def build_forecast_dataframe(
    delta_discharge,
    features,
    freq: str = "15min"
    ) -> pd.DataFrame:
    
    last_timestamp = features.index.max()
    last_discharge = features["discharge"].values
    
    forecast_index = pd.date_range(
        start=last_timestamp + pd.Timedelta(freq),
        periods=len(delta_discharge),
        freq=freq,
    )

    predicted_discharge = last_discharge + delta_discharge
    
    df = pd.DataFrame(
        {
            "predicted": predicted_discharge,
            # "model_version": model_version,
        },
        index=forecast_index,
    )

    df.index.name = "timestamp"

    return df


def merge_data(
    dfs: list[pd.DataFrame]
    ) -> pd.DataFrame:
    
    df_merged = pd.concat(
        dfs,
        axis=1,
        join="outer"
        )
    
    return df_merged#.dropna(axis="index")
    



def main() -> None:
    discharge = load_discharge_data(days=7)
    precip_observation = load_precip_observation_data(days=7)
    
    dfs = [discharge, precip_observation]
    
    merged = merge_data(dfs=dfs)
    
    features = create_inference_features(df=merged)
    
    inference = run_inference(df=features)
    
    df_inference = build_forecast_dataframe(
        delta_discharge=inference,
        features=features,
        freq="15min"
    )
    
    write_to_db(df_inference)

        
if __name__ == "__main__":
    main()