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
    

def build_precip_timeseries(
    input_dir: str | Path,
    catchment_path: str | Path,
    clip_crs: str
    ) -> pd.DataFrame:
    
    input_dir = Path(input_dir)
    
    catchment = gpd.read_file(catchment_path).to_crs(clip_crs)
    file_paths = sorted(input_dir.glob("*.grib2"))
    
    dfs: list[pd.DataFrame] = []
    
    
    for file in file_paths:
        try:
            ds = xr.open_dataset(file, engine="cfgrib")

            precip_crop = clip_to_catchment(
                dataset=ds,
                catchment=catchment,
                crs=clip_crs
            )

            df_precip = extract_precip_timeseries(precip=precip_crop)
            
            dfs.append(df_precip)
        
        except Exception:
            logger.exception("Failed to open GRIB file: %s", file)
            continue
        
        finally:
            ds.close()
        
        
        if not dfs:
            raise ValueError("No valid precipitation files processed.")
        
        
    df = pd.concat(dfs)
    
    df = (
        df
        .sort_index()
        .drop_duplicates()
    )
    
    df.index.name = "timestamp"

    # cumulative → incremental precipitation
    df["precip_mean"] = df["precip_cum_mean"].diff()

    df = (
        df
        .drop(columns=["precip_cum_mean"])
        .dropna()
    )

    return df