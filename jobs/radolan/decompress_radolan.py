from pathlib import Path
import shutil
import tarfile
import pandas as pd

from configs import settings
from utils.logger import logger


radolan_settings = settings.ingestion.radolan


def extract_radolan_timestamp(
    file_path: str | Path
    ) -> pd.Timestamp:
    
    stem = Path(file_path).stem
    
    _, back = stem.split("-")

    timestring = Path(back).name.removesuffix(".tar")
    
    observation_time = pd.to_datetime(timestring, format="%y%m%d")
    
    return observation_time


def decompress_tar_file(
    source_path: str | Path,
    target_dir: str | Path,
    ) -> Path:
    
    source_path = Path(source_path)
    target_dir = Path(target_dir)


    with tarfile.open(source_path, mode="r:gz") as tar:
        tar.extractall(path=target_dir)

    return target_dir



def decompress_tar_dir(
    input_dir: str | Path,
    output_dir: str | Path,
    days: int
    ) -> None:
    
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    
    # Decompress only specific timedelta
    cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)
    
    file_paths = [
        p for p in input_dir.rglob("*.tar.gz")
        if extract_radolan_timestamp(p) >= cutoff
    ]
    
    logger.info("Found %s files to decompress", len(file_paths))
    
    
    decompressed_count = 0
    
    for source_path in file_paths:
        target_name = Path(source_path.stem).stem
        target_dir = output_dir / target_name
        
        if target_dir.exists():
            logger.info("Skipping existing file: %s", target_name)
            continue
        
        
        decompress_tar_file(
            source_path=source_path, 
            target_dir=target_dir
        )
        
        decompressed_count += 1

    logger.info("Decompressed %s files", decompressed_count)


if __name__ == "__main__":
    decompress_tar_dir(
        input_dir=radolan_settings.compressed_dir,
        output_dir=radolan_settings.decompressed_dir,
        days=30
    )