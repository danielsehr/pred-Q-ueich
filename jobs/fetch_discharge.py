import requests
import pandas as pd

URL = (
    "https://geodaten-wasser.rlp-umwelt.de/"
    "api/data/messstellen_wasserstand_abflusswerte_30"
    "?w=messstellennummer=2377050700"
)

HEADERS  = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://geodaten-wasser.rlp-umwelt.de/",
}

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