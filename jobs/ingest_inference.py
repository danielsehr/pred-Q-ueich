from sqlalchemy.orm import Session

from database.db import SessionLocal
from database.models import Inference
from database.queries import load_discharge_data
from model.features import create_features
from model.inference import run_inference
import pandas as pd


def write_to_db(df) -> None:
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
    
    except Exception:
        session.rollback()
        raise
        
    finally:
        session.close()
        
        
def build_forecast_dataframe(
    preds,
    history_index,
    freq: str = "1h"
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
    
    features = create_features(df=discharge)
    features = features.drop(columns="target")
    latest_features = features.tail(1)
    
    inference = run_inference(df=latest_features)
    
    inference = build_forecast_dataframe(
        preds=inference,
        history_index=features.index,
        freq="1h"
    )
    
    write_to_db(inference)

    print(f"[INFERENCE] Inserted {len(inference)} rows.")

        
        
if __name__ == "__main__":
    main()