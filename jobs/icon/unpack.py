from pathlib import Path
import shutil
import bz2


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