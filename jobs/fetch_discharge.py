import requests
import pandas as pd

from configs.jobs_config import URL, HEADERS
from utils.logger import logger


def prepare_data(df):
    df = df.copy()
    
    df["datestring"] = pd.to_datetime(
        df["datum"], 
        format="%d.%m.%Y %H:%M"
        )

    df["abfluss"] = pd.to_numeric(
            df["abfluss"]
            .str.replace(",", ".", regex=False),
            errors="coerce"
        )
    
    df = (
        df[["datestring", "abfluss"]]
        .rename(columns={
            "datestring": "timestamp",
            "abfluss": "discharge"
            })
        .set_index("timestamp")
        .sort_index()
    )

    df = df.dropna(subset=["discharge"])
    
    return df


def fetch():
    try:
        response = requests.get(URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
    
        df = pd.DataFrame(response.json())

        return prepare_data(df)
        
    except requests.RequestException as e:
        logger.exception("Failed to fetch discharge data: %s", response)
        raise