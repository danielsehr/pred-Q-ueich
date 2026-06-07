from pathlib import Path
import shutil
import bz2

from configs import settings
from utils.logger import logger


icon_settings = settings.ingestion.icon


def decompress_bz2_file(
    source_path: str | Path,
    target_path: str | Path | None = None,
    ) -> Path:
    
    source_path = Path(source_path)

    if target_path is None:
        target_path = source_path.with_suffix("")

    target_path = Path(target_path)
    
    try:
        with bz2.open(source_path, "rb") as source:
            with open(target_path, "wb") as target:
                shutil.copyfileobj(source, target)
                
    except OSError:
        logger.exception(
            "Failed to decompress %s", source_path
        )
        raise
        
    
    return target_path


def decompress_bz2_dir(
    input_dir: str | Path,
    output_dir: str | Path
    ) -> None:
    
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)

    file_paths = [p for p in input_dir.rglob("*.grib2.bz2")]


    decompressed_count = 0
    
    for source_path in file_paths:
        target_name = source_path.stem
        target_path = output_dir / target_name
        
        if target_path.exists():
            # logger.info("Skipping existing file: %s", target_name)
            continue
        
        try:
            decompress_bz2_file(
                source_path=source_path, 
                target_path=target_path
            )
        
        except OSError:
            continue
        
        decompressed_count += 1

    logger.info("Decompressed %s files", decompressed_count)



if __name__ == "__main__":
    decompress_bz2_dir(
        input_dir=icon_settings.compressed_dir,
        output_dir=icon_settings.decompressed_dir
    )
    
