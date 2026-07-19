from discharge_queich.configs import settings
from discharge_queich.jobs.radolan_hourly.fetch_radolan import fetch_radolan
from discharge_queich.jobs.radolan_hourly.process_radolan import build_precip_timeseries
from discharge_queich.database.queries.radolan_hourly import IngestionResult, get_latest_timestamp, write_to_db

radolan_settings = settings.ingestion.radolan_hourly


def ingest_radolan() -> IngestionResult: 
    fetch_radolan()
    
    latest_ts = get_latest_timestamp()
    
    df_precip_mean = build_precip_timeseries(
        input_dir=radolan_settings.compressed_dir,
        catchment_path=settings.ingestion.catchment.catchment_path,
        start=latest_ts
    )
    
    ingestion_result = write_to_db(df_precip_mean)
    
    return ingestion_result