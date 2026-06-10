from pydantic import BaseModel


class DashboardSettings(BaseModel):
    api_url: str
    refresh_interval: int
    default_dashboard_days: int
 