from pathlib import Path
import shutil
import tarfile

from configs.jobs_config import ICON_OUTPUT_DIR, DECOMPRESSED_DIR
from utils.logger import logger


def decompress_tar_file(
    source_path: str | Path,
    target_dir: str | Path,
    ) -> Path:
    
    source_path = Path(source_path)
    target_dir = Path(target_dir)
    # folder_name = Path(source_path.stem).stem
    
    # target_dir = Path(target_dir) / folder_name
    # target_dir.mkdir(parents=True, exist_ok=True)


    with tarfile.open(source_path, mode="r:gz") as tar:
        tar.extractall(path=target_dir)

    return target_dir


def decompress_tar_dir(
    input_dir: str | Path,
    output_dir: str | Path
    ) -> None:
    
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    file_paths = [p for p in input_dir.rglob("*.tar.gz")]
    
    
    decompressed_count = 0
    
    for source_path in file_paths[:5]:
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
        input_dir=ICON_OUTPUT_DIR,
        output_dir=DECOMPRESSED_DIR
    )