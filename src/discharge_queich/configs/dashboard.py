from pydantic_settings import BaseSettings


class DashboardSettings(BaseSettings):
    api_url: str
    refresh_interval: int
    default_dashboard_days: int
 