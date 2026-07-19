from discharge_queich.jobs.discharge.fetch_discharge import fetch_discharge
from discharge_queich.database.queries.discharge import IngestionResult, get_last_timestamp, write_to_db


def ingest_discharge() -> IngestionResult:
    df = fetch_discharge()
    
    ingestion_result = write_to_db(df)
    
    return ingestion_result