from dataclasses import dataclass
from pathlib import Path
import pandas as pd



@dataclass(slots=True)
class IconMetadata:
    file_path: str | Path
    file_name: str | Path
    run_time: pd.Timestamp
    lead_hour: int
    valid_time: pd.Timestamp


def parse_icon_filepath(filepath: str | Path) -> IconMetadata:
    
    filename = Path(filepath).stem
    split = str(filename).split("_")    
    
    run_time = pd.to_datetime(split[4], format="%Y%m%d%H")
    lead_hour = int(split[5])

    return IconMetadata(
        file_path=filepath,
        file_name=filename,
        run_time=run_time,
        lead_hour=lead_hour,
        valid_time=run_time + pd.Timedelta(hours=lead_hour),
    )
    

def get_local_metadata(input_dir: str | Path) -> pd.DataFrame:
    
    input_dir = Path(input_dir)
    file_paths = sorted(input_dir.glob("*.grib2"))

    rows = []
    
    for path in file_paths:
        temp = parse_icon_filepath(filepath=path)
        
        rows.append({
            "file_path": temp.file_path,
            "file_name": temp.file_name,
            "run_time": temp.run_time,
            "lead_hour": temp.lead_hour,
            "valid_time": temp.valid_time + pd.Timedelta(hours=temp.lead_hour)
        })

    return pd.DataFrame(rows)
    

def filter_icon_files(
    df: pd.DataFrame,
    timestamp: pd.Timestamp | None
    ) -> pd.DataFrame:
    
    if timestamp is None:
        return df
    
    df = df[df["timestamp"] >= timestamp]
    
    return df