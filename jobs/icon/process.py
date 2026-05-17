from pathlib import Path
import pandas as pd
import geopandas as gpd
import xarray as xr

from configs.jobs_config import DECOMPRESSED_DIR
from utils.logger import logger


def clip_to_catchment(
    dataset: xr.Dataset,
    catchment: gpd.GeoDataFrame,
    crs: str
    ) -> xr.Dataset:
    
    if "tp" in dataset:
        precip = dataset["tp"]
    
    # Check CRS
    precip = precip.rio.write_crs(crs)
    assert precip.rio.crs == catchment.crs
    
    
    # --- Crop bounding box of catchment ---
    minx, miny, maxx, maxy = catchment.total_bounds

    precip_crop = precip.rio.clip_box(
        minx=minx,
        miny=miny,
        maxx=maxx,
        maxy=maxy,
    )
    
    # # --- Optional geometry clip ---
    # precip_masked = precip_cropped.rio.clip(
    #     catchment.geometry,
    #     catchment.crs,
    #     drop=False,
    # )
    
    return precip_crop  


def extract_precip_timeseries(
    precip: xr.Dataset,
    ) -> pd.DataFrame:
    
    rows = []

    for i in range(len(precip.step)):
        
        precip_step = precip.isel(step=i)
        
        forecast_time = pd.to_datetime(precip_step.valid_time.values)
        precip_cum_mean = float(precip_step.mean())
        
        rows.append({
            "timestamp": forecast_time,
            "precip_cum_mean": precip_cum_mean
        })
        
    df = pd.DataFrame(rows)
    df = df.set_index("timestamp")
    
    return df
    
