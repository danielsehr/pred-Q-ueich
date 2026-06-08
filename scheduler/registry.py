from jobs.icon.ingest_icon import main as ingest_precip_forecast
from jobs.radolan.ingest_radolan import main as ingest_precip_observation
from jobs.radolan_hourly.ingest_radolan import main as ingest_precip_hourly_observation

from scheduler.jobs import ingest_discharge_and_inference


JOB_REGISTRY = {
    "ingest_discharge_and_inference": ingest_discharge_and_inference,
    "ingest_precip_forecast": ingest_precip_forecast,
    "ingest_precip_observation": ingest_precip_observation,
    "ingest_precip_hourly_observation": ingest_precip_hourly_observation
}