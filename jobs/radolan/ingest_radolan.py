import pandas as pd

from sqlalchemy.orm import Session
from database.db import SessionLocal
from database.models import RadolanPrecipObservation

from configs.jobs_config import RADOLAN_OUTPUT_DIR, RADOLAN_DECOMPRESSED_DIR, CATCHMENT_PATH
from utils.logger import logger
from jobs.radolan.fetch_radolan import fetch_radolan
from jobs.radolan.decompress_radolan import decompress_tar_dir
from jobs.radolan.process_radolan import build_precip_timeseries


def write_to_db(df: pd.DataFrame) -> None:
    session: Session = SessionLocal()
    
    try:
        for timestamp, row in df.iterrows():
            
            entry = RadolanPrecipObservation(
                timestamp=timestamp,
                precip_mean=row["precip_mean"]
            )
            
            session.merge(entry)
            
        session.commit()
        
        logger.info("[RADOLAN PRECIP OBSERV] Inserted %s rows.", len(df))

    
    except Exception:
        session.rollback()
        logger.exception("[RADOLAN PRECIP OBSERV] Failed DB ingestion.")
        raise
    
    
    finally:
        session.close()
        


def main() -> None: 
    fetch_radolan()
    
    decompress_tar_dir(
        input_dir=RADOLAN_OUTPUT_DIR,
        output_dir=RADOLAN_DECOMPRESSED_DIR
    )
    
    # df_precip_mean = build_precip_timeseries(
    #     input_dir=RADOLAN_DECOMPRESSED_DIR,
    #     catchment_path=CATCHMENT_PATH
    # )
    
    # write_to_db(df_precip_mean)
    
    
if __name__ == "__main__":
    main()
    
    
    
    