from dataclasses import dataclass

from tqdm import tqdm
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup, Tag
import pandas as pd

from discharge_queich.configs import settings
from discharge_queich.utils.logger import logger

from discharge_queich.jobs.icon.dataclasses import IconDownloadFiles 

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
    
    
def fetch_remote_metadata(url: str | Path) -> pd.DataFrame:
    try:
        response = requests.get(str(url), timeout=30)
        response.raise_for_status()

    except requests.RequestException as e:
        logger.exception("[ICON PRECIP FORECAST] Fail in request metadata from %s", url)
        raise
        
        
    rows = []
    
    soup = BeautifulSoup(response.text, "html.parser")

    for a in soup.find_all("a"):

        href = str(a.get("href"))
        
        if(
            href is None
            or "lat-lon" not in href
            or not href.endswith(".grib2.bz2")
        ):
            continue

        filename = Path(href).stem
        split = str(filename).split("_")    
        
        run_time = pd.to_datetime(split[4], format="%Y%m%d%H")
        lead_hour = int(split[5])
        
        upload_time = get_upload_time(html_tag=a)
        
        if upload_time is None:
            continue


        rows.append({
            "filename": href,
            "run_time": run_time,
            "lead_hour": lead_hour,
            "valid_time": run_time + pd.Timedelta(hours=lead_hour),
            "datetime_upload": upload_time,
            "url": url,
        })

    return pd.DataFrame(rows)

    
def get_local_filenames(path: str | Path) -> set[Path]:
    
    return {
        file for file in Path(path).glob("*.grib2.bz2")
    }
    

def get_missing_grib_files(
    df: pd.DataFrame,
    local_filenames: set
    ) -> pd.DataFrame:
    
    return df[~df["filename"].isin(local_filenames)]
    

def download_icon_file(
    root_url: str,
    file_name: str,
    output_dir: str | Path
    ) -> bool:
    
    file_url = urljoin(root_url, file_name)

    output_path = Path(output_dir) / file_name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if output_path.exists():
        return False


    try:
        with requests.get(file_url, timeout=30, stream=True) as r:
                    
            r.raise_for_status()

            with open(output_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        
        logger.info("[ICON PRECIP FORECAST] Saved %s to %s",file_name, output_path)
        
        return True        
        
        
    except requests.RequestException:
        logger.exception("[ICON PRECIP FORECAST] Failed downloading file: %s", file_url)
        raise
    
    except OSError:
        logger.exception("[ICON PRECIP FORECAST] Failed writing file: %s", output_path)
        raise
    

def fetch_icon() -> None:
    downloads = 0
    
    for url, output_dir in zip(
        icon_settings.urls,
        icon_settings.compressed_dirs,
        strict=True
        ):
        
        remote_metadata = fetch_remote_metadata(url=url)
        
        local_filename = get_local_filenames(path=output_dir)
        
        missing_files = get_missing_grib_files(
            df=remote_metadata,
            local_filenames=local_filename
        )
        
        for filename in missing_files["filename"]:
        
            downloaded = download_icon_file(
                root_url=url,
                file_name=filename,
                output_dir=output_dir
                )
    
            if downloaded:
                downloads += 1
            
    logger.info("[ICON PRECIP FORECAST] Downloaded %s new grib files!", downloads)