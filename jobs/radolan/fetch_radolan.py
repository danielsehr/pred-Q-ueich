from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup, Tag
import pandas as pd

# from configs.jobs_config import 
from utils.logger import logger 


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


def get_observation_date(href: str) -> pd.Timestamp:
    
    _, second = href.split("-")
    date, _ = second.split(".", maxsplit=1)
    
    return pd.to_datetime(date, format="%y%m%d")


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

            if "-hdf5-" in href:
                continue

            if not href.endswith(".tar.gz"):
                continue
            
            
            observation_date = get_observation_date(href=href)
            upload_time = get_upload_time(html_tag=a)
            
            if upload_time is None:
                continue
            
            
            rows.append({
                        "filename": href,
                        "datetime_observation": observation_date,
                        "datetime_upload": upload_time,
                    })

        
        return pd.DataFrame(rows)
        
        
    except requests.RequestException as e:
        logger.exception("Failed to fetch icon metadata from %s", url)
        raise
    

def get_local_forecast_times(directory: str | Path):
    directory = Path(directory)
    
    forecast_times = set()
    
    for file in directory.glob("*.tar.gz"):
        forecast_time = get_observation_date(href=file.name)
        
        forecast_times.add(forecast_time)
        
    return forecast_times


def download_radolan_file(
    root_url: str,
    file_name: str,
    output_dir: str
    ) -> None:
    
    file_url = urljoin(root_url, file_name)

    output_path = Path(output_dir) / file_name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if output_path.exists():
        logger.info("File %s yet exists, skip download", file_name)
        return
        
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
    