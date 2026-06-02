from tqdm import tqdm
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup, Tag
import pandas as pd

from configs import settings
from utils.logger import logger


icon_settings = settings.ingestion.icon


def get_upload_time(html_tag: Tag) -> pd.Timestamp | None:
    tail = str(html_tag.next_sibling)

    if tail is None:
        return None

    parts = tail.strip().split()

    upload_time = pd.to_datetime(
        f"{parts[0]} {parts[1]}",
        dayfirst=True
        # format="%d-%B-%Y %H:%M:%S"
    )
    
    return upload_time


def get_forecast_time(href: str) -> pd.Timestamp:
    split = href.split("_")
    
    date = split[4]
    hour = split[5]
    
    date = pd.to_datetime(date, format="%Y%m%d00")
    
    forecast_time = date + pd.Timedelta(hours=int(hour))
    
    return forecast_time


def fetch_icon_metadata(url: str | Path) -> pd.DataFrame:
    try:
        response = requests.get(str(url), timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        
        
        rows = []

        for a in soup.find_all("a"):

            # Get filename
            href = str(a.get("href"))
            
            if not href:
                continue

            if "lat-lon" not in href:
                continue

            if not href.endswith(".grib2.bz2"):
                continue


            # Get forecast time
            forecast_time = get_forecast_time(href=href)
            

            # Get upload time
            upload_time = get_upload_time(html_tag=a)
            
            if upload_time is None:
                continue


            # Writ to list
            rows.append({
                "filename": href,
                "datetime_forecast": forecast_time,
                "datetime_upload": upload_time,
            })

        
        return pd.DataFrame(rows)
        
        
    except requests.RequestException as e:
        logger.exception("Failed to fetch icon metadata from %s", url)
        raise
    

def get_local_forecast_times(directory: str | Path):
    directory = Path(directory)
    
    forecast_times = set()
    
    for file in directory.glob("*.grib2.bz2"):
        forecast_time = get_forecast_time(href=file.name)
        
        forecast_times.add(forecast_time)
        
    return forecast_times
    
    
def download_icon_file(
    root_url: str,
    file_name: str,
    output_dir: str
    ) -> None:
    
    file_url = urljoin(root_url, file_name)

    output_path = Path(output_dir) / file_name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        logger.info("Downloading %s", file_name)    
        
        with requests.get(file_url, timeout=30, stream=True) as r:
                    
            r.raise_for_status()

            with open(output_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        
        logger.info("Saved file to %s", output_path)
        
        
    except requests.RequestException:
        logger.exception("Failed downloading file: %s", file_url)
        raise
    
    except OSError:
        logger.exception("Failed writing file: %s", output_path)
        raise



def fetch_icon() -> None:
    
    df_remote = fetch_icon_metadata(url=icon_settings.url)
    local_times = get_local_forecast_times(directory=icon_settings.compressed_dir)

    df_missing = df_remote[
        ~df_remote["datetime_forecast"].isin(local_times)
    ]

    logger.info("Found %s new forecast files", len(df_missing))
    
    for _, row in df_missing.iterrows():

        download_icon_file(
            root_url=icon_settings.url,
            file_name=row["filename"],
            output_dir=icon_settings.compressed_dir,
        )


if __name__ == "__main__":
    fetch_icon()