from dataclasses import dataclass

from tqdm import tqdm
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup, Tag
import pandas as pd

from discharge_queich.configs import settings
from discharge_queich.utils.logger import logger


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
    
    # date = pd.to_datetime(date, format="%Y%m%d00")
    date = pd.to_datetime(date, format="%Y%m%d%H")
    
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
                "url": url,
            })

        
        return pd.DataFrame(rows)
        
        
    except requests.RequestException as e:
        logger.exception("Failed to fetch icon metadata from %s", url)
        raise
    

def get_local_forecast_times(directory: str | Path) -> set:
    directory = Path(directory)
    
    forecast_times = set()
    
    for file in directory.glob("*.grib2.bz2"):
        forecast_time = get_forecast_time(href=file.name)
        
        forecast_times.add(forecast_time)
        
    return forecast_times
    
    
def check_missing_grib_files(
    df: pd.DataFrame,
    local_times: set
    ) -> pd.DataFrame:
    
    df_missing = df[
        ~df["datetime_forecast"].isin(local_times)
    ]
    
    return df_missing



@dataclass(slots=True)
class IconDownloadFiles:
    run: str
    url: str
    output_dir: str | Path
    remote_metadata: pd.DataFrame | None
    local_times: set | None
    missing_files: pd.DataFrame| None
    filename: pd.DataFrame | pd.Series | None


def build_icon_download_dataclass() -> list[IconDownloadFiles]:
    runs = [
        IconDownloadFiles(
            run=Path(url).parent.stem,
            url=url,
            output_dir=directory,
            remote_metadata=None,
            local_times=None,
            missing_files=None,
            filename=None
        ) 
        for url, directory in zip(
            icon_settings.urls,
            icon_settings.compressed_dirs,
            strict=True,
        )
    ]
    
    for run in runs:
        run.remote_metadata = fetch_icon_metadata(url=run.url)
        
        run.local_times = get_local_forecast_times(directory=run.output_dir)
        
        run.missing_files = check_missing_grib_files(
            df=run.remote_metadata,
            local_times=run.local_times
        )
        
        run.filename = run.missing_files["filename"]
        
        if (len(run.missing_files) != 0):
            logger.info("[RADOLAN PRECIP HOURLY OBSERV] Found %s new files for run %s.", len(run.missing_files), run.run)
    
    return runs
    

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
        logger.info("Downloading %s", file_name)    
        
        with requests.get(file_url, timeout=30, stream=True) as r:
                    
            r.raise_for_status()

            with open(output_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        
        logger.info("Saved file to %s", output_path)
        
        return True        
        
        
    except requests.RequestException:
        logger.exception("Failed downloading file: %s", file_url)
        raise
    
    except OSError:
        logger.exception("Failed writing file: %s", output_path)
        raise


def download_all_icon_files(
    icon_files: list[IconDownloadFiles]
    ) -> None:
    
    downloads = 0
    
    for file in icon_files:
        if file.filename is not None:
            for name in file.filename :
                
                downloaded = download_icon_file(
                    root_url=file.url,
                    file_name=str(name),
                    output_dir=file.output_dir
                )
                
                if downloaded:
                    downloads += 1
                
    logger.info("Downloaded %s new files", downloads)


def fetch_icon() -> None:
    runs = build_icon_download_dataclass()

    download_all_icon_files(icon_files=runs)
