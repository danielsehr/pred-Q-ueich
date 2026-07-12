from pathlib import Path

import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup, Tag
import pandas as pd
from datetime import datetime

from dataclasses import dataclass

from sqlalchemy import select
from discharge_queich.database.db import SessionLocal
from discharge_queich.database.models import TempStationFileState

from src.discharge_queich.configs import settings
from src.discharge_queich.utils.logger import logger
from src.discharge_queich.jobs.temp.stations import STATIONS


temp_settings = settings.ingestion.temp


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
    

@dataclass
class TempFileState:
    station_id: str
    timestamp: pd.Timestamp
    etag: str | None
    last_modified: pd.Timestamp | None


def get_temp_file_state(
    url: str | Path
    ) -> TempFileState:
    
    station_id = Path(url).stem.split(sep="_")[2]
    
    try:
        response =  requests.head(str(url), allow_redirects=True)
        response.raise_for_status()
        
        
        timestamp = pd.to_datetime(
            str(datetime.now()),
            format="%Y-%m-%d %H:%M:%S.%f"
        )
        
        etag =  response.headers.get("ETag")
        
        last_modified =  response.headers.get("Last-Modified")
        last_modified = (
            pd.to_datetime(
            last_modified,
            utc=True
            ) if last_modified is not None
            else None
        )
        
        return TempFileState(
            station_id=station_id,
            timestamp=timestamp,
            etag=etag,
            last_modified=last_modified
        )
        
        
    except requests.RequestException as e:
        logger.exception("Failed to get request header from %s", url)
        raise



def get_last_file_state(
    station_id: str
    ) -> TempFileState | None:
    
    with SessionLocal() as session:
        
        stmt = (
            select(TempStationFileState)
            .where(TempStationFileState.station_id == station_id)
        )
        
        row = session.scalar(stmt)
        
        if row is None:
            return None
        
        return TempFileState(
            station_id = row.station_id,
            timestamp = pd.Timestamp(row.timestamp),
            etag = row.etag,
            last_modified = pd.Timestamp(row.last_modified)
        )



def ingest_temp_file_state(temp_file_state: TempFileState):
    
    with SessionLocal() as session:
        try:
            entry = TempStationFileState(
                station_id = temp_file_state.station_id,
                timestamp = temp_file_state.timestamp,
                etag = temp_file_state.etag,
                last_modified = temp_file_state.last_modified
            )
            
            session.merge(entry)
        
            session.commit()
            
            logger.info("[TEMP STAT FILE STATE] Inserted new file state.")
            
            return True
            
        
        except Exception:
            session.rollback()
            logger.exception("[TEMP STAT FILE STATE] Failed DB ingestion.")
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
        
        station_id = row["station_id"]
        file_url = row["file_url"]
        file_name = row["filename"]
        
        
        current_file_state = get_temp_file_state(url=file_url)
        last_file_state = get_last_file_state(station_id=station_id)

        if (
            last_file_state is not None 
            and current_file_state.etag == last_file_state.etag
            ):
            logger.info(
                "[TEMP STAT FILE STATE] No new file state detected for station %s.", 
                station_id
            )
            continue
        
        
        download_temp_file(
            url=file_url,
            file_name=file_name,
            output_dir=temp_settings.compressed_dir
        )
        
        ingest_temp_file_state(temp_file_state=current_file_state)