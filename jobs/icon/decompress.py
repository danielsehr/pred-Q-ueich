from pathlib import Path
import shutil
import bz2

from configs.jobs_config import ICON_OUTPUT_DIR, DECOMPRESSED_DIR
from utils.logger import logger


def decompress_bz2(
    source_path: str | Path,
    target_path: str | Path | None = None,
    ) -> Path:
    
    source_path = Path(source_path)

    if target_path is None:
        target_path = source_path.with_suffix("")

    target_path = Path(target_path)

    with bz2.open(source_path, "rb") as source:
        with open(target_path, "wb") as target:
            shutil.copyfileobj(source, target)

    return target_path


def main(
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
            logger.info("Skipping existing file: %s", target_name)
            continue
        
        
        decompress_bz2(
            source_path=source_path, 
            target_path=target_path
        )
        
        decompressed_count += 1

    logger.info("Decompressed %s files", decompressed_count)



if __name__ == "__main__":
    main(
        input_dir=ICON_OUTPUT_DIR,
        output_dir=DECOMPRESSED_DIR
    )
    
