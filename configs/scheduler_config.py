from jobs.ingest_discharge import main as ingest_discharge
from jobs.ingest_inference import main as ingest_inference
from jobs.icon.ingest_icon import main as ingest_precip_forecast


JOBS = [
    {
        "name": "ingest_discharge",
        "func": ingest_discharge,
        "interval_minutes": 10,
    },
    {
        "name": "ingest_inference",
        "func": ingest_inference,
        "interval_minutes": 10,
    },
    {
        "name": "ingest_precip_forecast",
        "func": ingest_precip_forecast,
        "interval_minutes": 10,
    },
]