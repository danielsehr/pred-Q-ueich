
import pandas as pd

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session

from discharge_queich.configs import settings
from discharge_queich.utils.logger import logger

from discharge_queich.jobs.icon.fetch import fetch_icon
from discharge_queich.jobs.icon.decompress import decompress_all_bz2_dirs
from discharge_queich.jobs.icon.process import process_icon
from discharge_queich.database.queries.icon import IngestionResult, write_to_db

icon_settings = settings.ingestion.icon


def ingest_icon() -> IngestionResult:
    fetch_icon()
    
    decompress_all_bz2_dirs()
    
    ingestion_result = IngestionResult()
    
    for path in icon_settings.decompressed_dirs:
        
        df = process_icon(runtime_dir=path)

        if df is None:
            continue
        
        ingestion_result += write_to_db(df=df)
    
    return ingestion_result