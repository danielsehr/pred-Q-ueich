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


@dataclass(slots=True)
class IconMetadata:
    run_time: pd.Timestamp
    lead_hour: int
    valid_time: pd.Timestamp
    

@dataclass(slots=True)
class IconDownloadFiles:
    run: str
    url: str
    output_dir: str | Path
    remote_metadata: pd.DataFrame | None
    local_filename: set[str] | set[Path] | None
    missing_files: pd.DataFrame| None


    
def parse_icon_filename(filename: str) -> IconMetadata:
    split = filename.split("_")    
    
    run_time = pd.to_datetime(split[4], format="%Y%m%d%H")
    lead_hour = int(split[5])

    return IconMetadata(
        run_time=run_time,
        lead_hour=lead_hour,
        valid_time=run_time.normalize() + pd.Timedelta(hours=lead_hour),
    )


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
            forecast_time = parse_icon_filename(filename=href)
            
            # Get upload time
            upload_time = get_upload_time(html_tag=a)
            
            if upload_time is None:
                continue


            # Writ to list
            rows.append({
                "filename": href,
                "run_time": forecast_time.run_time,
                "lead_hour": forecast_time.lead_hour,
                "valid_time": forecast_time.valid_time,
                "datetime_upload": upload_time,
                "url": url,
            })

        
        return pd.DataFrame(rows)
        
        
    except requests.RequestException as e:
        logger.exception("[ICON PRECIP FORECAST] Failed to fetch metadata from %s", url)
        raise
    
    
def get_local_filenames(
    path: str | Path
    ) -> set[str] | set[Path]:
    
    return {
        file for file in Path(path).glob("*.grib2.bz2")
    }
    

def get_missing_grib_files(
    df: pd.DataFrame,
    local_names: set
    ) -> pd.DataFrame:
    
    df_missing = df[
        ~df["filename"].isin(local_names)
    ]
    
    return df_missing
    
    
def build_icon_download_dataclass() -> list[IconDownloadFiles]:
    runs = [
        IconDownloadFiles(
            run=Path(url).parent.stem,
            url=url,
            output_dir=directory,
            remote_metadata=None,
            local_filename=None,
            missing_files=None,
        ) 
        for url, directory in zip(
            icon_settings.urls,
            icon_settings.compressed_dirs,
            strict=True,
        )
    ]
    
    
    for run in runs:
        run.remote_metadata = fetch_icon_metadata(url=run.url)
        
        run.local_filename = get_local_filenames(path=run.output_dir)
        
        run.missing_files = get_missing_grib_files(
            df=run.remote_metadata,
            local_names=run.local_filename
        )
    
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
    

def download_all_icon_file(icon_files: list[IconDownloadFiles]):
    
    downloads = 0
    
    for run in icon_files:
        if run.missing_files is None:
            continue
        
        for filename in run.missing_files["filename"]:
            downloaded = download_icon_file(
                root_url=run.url,
                file_name=filename,
                output_dir=run.output_dir
            )
        
        if downloaded:
            downloads += 1
            
    logger.info("[ICON PRECIP FORECAST] Downloaded %s new grib files!", downloads)
            
            
def fetch_icon() -> None:
    runs = build_icon_download_dataclass()
    
    download_all_icon_file(icon_files=runs)