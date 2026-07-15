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
from discharge_queich.jobs.icon.metadata import fetch_remote_metadata

icon_settings = settings.ingestion.icon
    
    
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