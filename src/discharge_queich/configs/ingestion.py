from pydantic_settings import BaseSettings


class CatchmentSettings(BaseSettings):
    catchment_path: str
    

class DischargeSettings(BaseSettings):
    url: str
    headers: dict[str, str]


class IconSettings(BaseSettings):
    url: str
    compressed_dir: str
    decompressed_dir: str
    clip_crs: str


class RadolanSettings(BaseSettings):
    url: str
    compressed_dir: str
    decompressed_dir: str
    
    
class RadolanHourlySettings(BaseSettings):
    url: str
    compressed_dir: str
    decompressed_dir: str


class TempStationSettings(BaseSettings):
    url: str
    stations_col_names: list[str]
    crs_4326: str
    crs_25832: str
    buffer_size: int
    stations_write_path: str
    
    
class IngestionSettings(BaseSettings):
    catchment: CatchmentSettings
    discharge: DischargeSettings
    icon: IconSettings
    radolan: RadolanSettings
    radolan_hourly: RadolanHourlySettings
    temp: TempStationSettings