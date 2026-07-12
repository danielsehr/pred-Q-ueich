from pathlib import Path

import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup, Tag
import pandas as pd
from datetime import datetime

from src.discharge_queich.configs import settings
from src.discharge_queich.utils.logger import logger
from src.discharge_queich.jobs.temp.stations import STATIONS


temp_settings = settings.ingestion.temp_recent


def get_upload_time(html_tag: Tag) -> pd.Timestamp | None:

    tail = str(html_tag.next_sibling)
    
    if tail is None:
        return None
    
    parts = tail.strip().split()
    
    upload_time = pd.to_datetime(
        f"{parts[0]} {parts[1]}",
        dayfirst=True
    )
    
    return upload_time


def get_station_id(href: str) -> str:
    
    _, _, station_id, _ = href.split("_", maxsplit=3)
    
    return station_id


def fetch_temp_metadata(
    url: str | Path,
    station_ids: list[str],
    ) -> pd.DataFrame:
    
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

            if not href.endswith(".zip"):
                continue
            
            if all(station not in href for station in station_ids):
                continue
            
            file_url = urljoin(str(url), href)
            station_id = get_station_id(href=href)
            upload_time = get_upload_time(html_tag=a)
            
            if upload_time is None:
                continue
            
            
            rows.append({
                        "station_id": station_id,
                        "filename": href,
                        "file_url": file_url,
                        "datetime_upload": upload_time,
                    })

        return pd.DataFrame(rows)
    
    
    except requests.RequestException as e:
        logger.exception("Failed to fetch icon metadata from %s", url)
        raise



def download_temp_file(
    url: str,
    file_name: str,
    output_dir: str
    ) -> None:
    
    output_path = Path(output_dir) / file_name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    
    try:
        logger.info("Downloading %s", file_name)    
        
        with requests.get(url, timeout=30, stream=True) as r:
                    
            r.raise_for_status()

            with open(output_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        
        logger.info("Saved file to %s", output_path)
        
        
    except requests.RequestException:
        logger.exception("Failed downloading file: %s", url)
        raise
    
    
    except OSError:
        logger.exception("Failed writing file: %s", output_path)
        raise
    
    

def fetch_temp() -> None:
    
    df_remote = fetch_temp_metadata(
        url=temp_settings.url, 
        station_ids=STATIONS
        )
    
    for _, row in df_remote.iterrows():
    
        # station_id = row["station_id"]
        file_url = row["file_url"]
        file_name = row["filename"]
    
        download_temp_file(
            url=file_url,
            file_name=file_name,
            output_dir=temp_settings.compressed_dir
        )
