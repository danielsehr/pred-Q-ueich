from src.jobs.discharge.ingest_discharge import main as ingest_discharge
from src.jobs.inference.ingest_inference import main as ingest_inference


def ingest_discharge_and_inference() -> None:

    inserted = ingest_discharge()

    if inserted:
        ingest_inference()