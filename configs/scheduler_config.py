from jobs.discharge.ingest_discharge import main as ingest_discharge
from jobs.inference.ingest_inference import main as ingest_inference
from jobs.icon.ingest_icon import main as ingest_precip_forecast
from jobs.radolan.ingest_radolan import main as ingest_precip_observation


JOBS = [
    {
        "name": "ingest_inference",
        "func": ingest_inference,
        "interval_minutes": 5,
    },
    {
        "name": "ingest_discharge",
        "func": ingest_discharge,
        "interval_minutes": 10,
    },
    {
        "name": "ingest_precip_forecast",
        "func": ingest_precip_forecast,
        "interval_minutes": 10,
    },
    {
        "name": "ingest_precip_observation",
        "func": ingest_precip_observation,
        "interval_minutes": 10,
    },
]