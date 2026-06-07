from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup, Tag
import pandas as pd

from configs import settings
from utils.logger import logger 


radolan_settings = settings.ingestion.radolan


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


def fetch_radolan_metadata(url: str | Path) -> pd.DataFrame:
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
    

def get_local_observation_date(directory: str | Path):
    directory = Path(directory)
    
    observation_dates = set()
    
    for file in directory.glob("*.tar.gz"):
        observation_date = get_observation_date(href=file.name)
        
        observation_dates.add(observation_date)
        
    return observation_dates


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
    
    
    
def fetch_radolan() -> None:
    
    df_remote = fetch_radolan_metadata(url=radolan_settings.url)
    local_times = get_local_observation_date(directory=radolan_settings.compressed_dir)

    df_missing = df_remote[
        ~df_remote["datetime_observation"].isin(local_times)
    ]

    logger.info("Found %s new precip observation files", len(df_missing))
    
    files = 0
    for _, row in df_missing.iterrows():

        download_radolan_file(
            root_url=radolan_settings.url,
            file_name=row["filename"],
            output_dir=radolan_settings.compressed_dir,
        )
        
        files += 1

    logger.info("Downloaded %s new precip observation files", files)


if __name__ == "__main__":
    fetch_radolan()