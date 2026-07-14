from dataclasses import dataclass
from pathlib import Path
import pandas as pd


@dataclass(slots=True)
class IconMetadata:
    file_path: str | Path
    file_name: str
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