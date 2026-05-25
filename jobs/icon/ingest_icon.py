import pandas as pd

from sqlalchemy.orm import Session
from database.db import SessionLocal
from database.models import IconPrecipForecast

from configs.jobs_config import ICON_OUTPUT_DIR, DECOMPRESSED_DIR, CATCHMENT_PATH, CLIP_CRS
from utils.logger import logger

from jobs.icon.process import build_precip_timeseries
from jobs.icon.decompress import decompress_bz2_dir
from jobs.icon.fetch_icon import fetch_icon


def write_to_db(df: pd.DataFrame) -> None:
    session: Session = SessionLocal()
    
    try:
        for timestamp, row in df.iterrows():
            
            entry = IconPrecipForecast(
                timestamp=timestamp,
                precip_mean=row["precip_mean"]
            )
            
            session.merge(entry)
        
        session.commit()
        
        logger.info("[ICON PRECIP FORECAST] Inserted %s rows.", len(df))
        
        
    except Exception:
        session.rollback()
        logger.exception("[ICON PRECIP FORECAST] Failed DB ingestion.")
        raise
    
    
    finally:
        session.close()
        
        

def main() -> None:
    fetch_icon()
    
    decompress_bz2_dir(
        input_dir=ICON_OUTPUT_DIR,
        output_dir=DECOMPRESSED_DIR
    )
    
    df_precip_mean = build_precip_timeseries(
        input_dir=DECOMPRESSED_DIR,
        catchment_path=CATCHMENT_PATH,
        clip_crs=CLIP_CRS
    )
    
    write_to_db(df_precip_mean)
    
    
if __name__ == "__main__":
    main()