from sqlalchemy.orm import Session
import pandas as pd

from utils.logger import logger
from database.db import SessionLocal
from database.models import Inference
from database.queries import load_discharge_data
from model.features import create_inference_features
from model.inference import run_inference


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
    preds,
    history_index,
    freq: str = "15min"
    ):
    
    last_timestamp = history_index[-1]
    
    forecast_index = pd.date_range(
        start=last_timestamp + pd.Timedelta(freq),
        periods=len(preds),
        freq=freq,
    )

    df = pd.DataFrame(
        {
            "predicted": preds,
            # "model_version": model_version,
        },
        index=forecast_index,
    )

    df.index.name = "timestamp"

    return df



def main() -> None:
    discharge = load_discharge_data()
    
    features = create_inference_features(df=discharge)
    
    inference = run_inference(df=features)
    
    inference = build_forecast_dataframe(
        preds=inference,
        history_index=features.index,
        freq="15min"
    )
    
    write_to_db(inference)

        
if __name__ == "__main__":
    main()