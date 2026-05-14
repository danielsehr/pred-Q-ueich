import requests
import pandas as pd
from jobs.config import URL, HEADERS


def prepare_data(df):
    df = df.dropna(subset=["abfluss"])
    
    df["datestring"] = pd.to_datetime(df["datestring"])

    df["abfluss"] = (
            df["abfluss"]
            .str.replace(",", ".", regex=False)
            .pipe(pd.to_numeric)
            .dropna()
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

    return df


def fetch():
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    
    df = pd.DataFrame(response.json())

    return prepare_data(df)