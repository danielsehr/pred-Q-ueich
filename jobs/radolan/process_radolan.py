from tqdm import tqdm
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd

import wradlib as wrl
import xarray as xr

from utils.logger import logger



def read_radolan_data(
    file_path: str | Path
    ) -> tuple[np.ndarray, dict]:
    
    file_path = Path(file_path)
    
    try:
        data, attrs = wrl.io.read_radolan_composite(file_path)
        
        data = np.array(data).astype(float)
        data = np.where(data == -9999, np.nan, data)
    
    except Exception:
        logger.exception("Failed to open RADOLAN BIN file: %s", file_path)
        raise
        
    return data, attrs


def extract_radolan_timestamp(
    file_path: str | Path
    ) -> pd.Timestamp:
    
    stem = Path(file_path).stem
    
    _, back = stem.split("_")
    _, timestring, _ = back.split("-", maxsplit=2)
    
    observation_time = pd.to_datetime(timestring, format="%y%m%d%H%M")
    
    return observation_time


def extract_radolan_coords(
    attrs: dict
    ) -> tuple[np.ndarray, np.ndarray]:
    
    grid = wrl.georef.get_radolan_grid(
        attrs["nrow"],
        attrs["ncol"]
    )
    
    x2d = np.array(grid)[:, :, 0]
    y2d = np.array(grid)[:, :, 1]
    
    return x2d, y2d


def radolan_to_xarray(
    file_path: str | Path
    ) -> xr.DataArray:
    
    data, attrs = read_radolan_data(file_path=file_path)
    
    observation_time = extract_radolan_timestamp(file_path=file_path)
    
    x2d, y2d = extract_radolan_coords(attrs=attrs)
    
    
    data_xr = xr.DataArray(
        data[np.newaxis, :, :],
        dims=("time", "y", "x"),
        coords={
            "time": [observation_time],
            "x": x2d[0, :],
            "y": y2d[:, 0],
            },
        name="precip"
        )
    
    data_xr = (
        data_xr
        .rio.set_spatial_dims(x_dim="x", y_dim="y")
        .rio.write_crs(wrl.georef.projection.create_crs("dwd-radolan"))
        )  

    return data_xr


def clip_to_catchment(
    dataset: xr.DataArray,
    catchment: gpd.GeoDataFrame,
    ) -> xr.DataArray:
    
    precip = dataset
    
    # Check CRS
    catchment = catchment.to_crs(dataset.rio.crs)
    
    
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
    file_path: str | Path,
    catchment: gpd.GeoDataFrame,
    ) -> dict:
    
    data_xr = radolan_to_xarray(file_path=file_path)
    
    precip_clipped = clip_to_catchment(
        dataset=data_xr,
        catchment=catchment,
        )

    observed_time = pd.to_datetime(precip_clipped.time.item())
    precip_mean = float(precip_clipped.mean(skipna=True) * 100) # 1/100 mm -> https://www.dwd.de/DE/leistungen/radolan/produktuebersicht/radolan_produktuebersicht_pdf.pdf;jsessionid=71FEFFEE6E0734198012B200CEDA6BD3.live11043?__blob=publicationFile&v=13

    row = {
        "timestamp": observed_time,
        "precip_cum_mean": precip_mean
        }
    
    
    return row


def build_precip_timeseries(
    input_dir: str | Path,
    catchment_path: str | Path,
    ) -> pd.DataFrame:
    
    input_dir = Path(input_dir)
    
    catchment = gpd.read_file(catchment_path)
    file_paths = sorted(input_dir.rglob("*--bin"))
    file_paths = file_paths[:600]
    
    
    # --- Extract dataset ---
    dfs = []
    
    for path in tqdm(file_paths, desc="Processing files"):
        try:
            dict_precip = extract_precip_timeseries(
                file_path=path,
                catchment=catchment
            )
            
            dfs.append(dict_precip)
            
        except Exception:
            logger.exception("Failed to process RADOLAN BIN file %s:", path)
            continue
    
    
    # --- Process dataframe ---
    df = pd.DataFrame.from_records(dfs)
    
    df = df.set_index("timestamp")
    df = df.sort_index()
    df = df[~df.index.duplicated(keep="last")]
            
            
    return df