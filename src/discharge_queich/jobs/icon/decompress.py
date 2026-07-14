from pathlib import Path
import shutil
import bz2

from discharge_queich.configs import settings
from discharge_queich.utils.logger import logger


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


    decompressed_count = 0
    
    for source_path in input_dir.rglob("*.grib2.bz2"):
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
        
        except Exception:
            logger.error("[ICON PRECIP FORECAST] Failed decompress grib file")
            raise
        
        decompressed_count += 1

    logger.info("[ICON PRECIP FORECAST] Decompressed %s files", decompressed_count)


def decompress_all_bz2_dirs() -> None:
    for compressed_dir, decompressed_dir in zip(
        icon_settings.compressed_dirs,
        icon_settings.decompressed_dirs,
        strict=True
        ):
        
        logger.info("[ICON PRECIP FORECAST] Decompressing %s -> %s", compressed_dir, decompressed_dir)
        
        decompress_bz2_dir(
            input_dir=compressed_dir,
            output_dir=decompressed_dir
        )
