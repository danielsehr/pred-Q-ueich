from pathlib import Path
import pandas as pd
import geopandas as gpd
import xarray as xr

from discharge_queich.configs import settings
from discharge_queich.utils.logger import logger

from discharge_queich.database.queries.icon import get_latest_runtime

catchment_settings = settings.ingestion.catchment
icon_settings = settings.ingestion.icon


def get_local_metadata(input_dir: str | Path) -> pd.DataFrame:
    
    input_dir = Path(input_dir)
    file_paths = sorted(input_dir.glob("*.grib2"))

    rows = []
    
    for path in file_paths:
        
        file_name = Path(path).stem
        split = str(file_name).split("_")    
        run_time = pd.to_datetime(split[4], format="%Y%m%d%H")
        lead_hour = int(split[5])
        
        rows.append({
            "file_path": path,
            "file_name": file_name,
            "run_time": run_time,
            "lead_hour": lead_hour,
            "valid_time": run_time + pd.Timedelta(hours=lead_hour)
        })

    return pd.DataFrame(rows)
    

def filter_icon_files(
    df: pd.DataFrame,
    latest_runtime: pd.Timestamp | None
    ) -> pd.DataFrame:
    
    if latest_runtime is None:
        return df
    
    df = df[df["run_time"] >= latest_runtime]
    
    return df


def clip_to_catchment(
    dataset: xr.Dataset,
    catchment: gpd.GeoDataFrame,
    crs: str
    ) -> xr.DataArray:
    
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
    precip: xr.DataArray,
    run_time: pd.Timestamp,
    ) -> pd.DataFrame:

    spatial_dims = [
        d for d in precip.dims
        if d not in {"step", "time"}
    ]

    ts = precip.mean(
        dim=spatial_dims,
        skipna=True,
    )

    # Normalize scalar → 1D
    if ts.ndim == 0:
        ts = ts.expand_dims(
            valid_time=[pd.to_datetime(ts.valid_time.values)]
        )

    df = (
        ts
        .to_dataframe(name="precip_cum_mean")
        .reset_index()
        .rename(columns={"valid_time": "timestamp"})
        )
    
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["run_time"] = run_time

    return df[["run_time", "timestamp", "precip_cum_mean"]]
    

def build_precip_timeseries(
    files: pd.DataFrame,
    catchment_path: str | Path,
    clip_crs: str,
    ) -> pd.DataFrame:
    
    catchment = gpd.read_file(catchment_path).to_crs(clip_crs)
    
    dfs: list[pd.DataFrame] = []
    
    for row in files.itertuples(index=False):
        ds = None
        
        try:
            ds = xr.open_dataset(
                row.file_path,
                # row["file_path"],
                engine="cfgrib",
                backend_kwargs={"indexpath": ""},
                )

            precip_crop = clip_to_catchment(
                dataset=ds,
                catchment=catchment,
                crs=clip_crs
            )

            df_precip = extract_precip_timeseries(
                precip=precip_crop,
                run_time=row.run_time
                # run_time=row["run_time"]
                )
            
            dfs.append(df_precip)
        
        
        except Exception:
            logger.exception("Failed to process ICON GRIB file: %s", row.file_path)
            continue
        
        
        finally:
            if ds is not None:
                ds.close()
                
    if not dfs:
        raise ValueError("No valid precipitation files processed.") 
    
    df = pd.concat(dfs)
    
    df = df.set_index("timestamp")
    df = df.sort_index()
    
    df["precip_mean"] = (
        df.groupby("run_time")["precip_cum_mean"]
        .diff()
        .fillna(df["precip_cum_mean"])
    )
    
    df = df.drop(columns=["precip_cum_mean"])
    
    return df


def process_icon(runtime_dir: str | Path) -> pd.DataFrame | None:
    
    latest_ts = get_latest_runtime()
    
    local_metadata = get_local_metadata(input_dir=runtime_dir)
    
    filtered = filter_icon_files(df=local_metadata, latest_runtime=latest_ts)
    
    if filtered.empty:
        return
    
    df = build_precip_timeseries(
        files=filtered,
        catchment_path=catchment_settings.catchment_path,
        clip_crs=icon_settings.clip_crs
        )

    return df