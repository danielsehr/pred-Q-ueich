from pydantic import BaseModel


class CatchmentSettings(BaseModel):
    catchment_path: str
    

class DischargeSettings(BaseModel):
    url: str
    headers: dict[str, str]


class IconSettings(BaseModel):
    url: str
    compressed_dir: str
    decompressed_dir: str
    clip_crs: str


class RadolanSettings(BaseModel):
    url: str
    compressed_dir: str
    decompressed_dir: str


class TempStationSettings(BaseModel):
    url: str
    stations_col_names: list[str]
    crs_4326: str
    crs_25832: str
    buffer_size: int
    stations_write_path: str
    
    
class IngestionSettings(BaseModel):
    catchment: CatchmentSettings
    discharge: DischargeSettings
    icon: IconSettings
    radolan: RadolanSettings
    temp: TempStationSettings