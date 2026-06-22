from pathlib import Path
import pandas as pd
import geopandas as gpd
import xarray as xr

from discharge_queich.utils.logger import logger



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
        .set_index("valid_time")[["precip_cum_mean"]]
    )

    df.index = pd.to_datetime(df.index)
    df.index.name = "timestamp"

    return df
    

def build_precip_timeseries(
    input_dir: str | Path,
    catchment_path: str | Path,
    clip_crs: str,
    ) -> pd.DataFrame:
    
    input_dir = Path(input_dir)
    
    file_paths = sorted(input_dir.glob("*.grib2"))
    
    catchment = gpd.read_file(catchment_path).to_crs(clip_crs)
    
    dfs: list[pd.DataFrame] = []
    
    # --- Open dataset and extract ---
    for file in file_paths:
        ds = None
        
        try:
            ds = xr.open_dataset(
                file, 
                engine="cfgrib",
                backend_kwargs={"indexpath": ""},
                )

            precip_crop = clip_to_catchment(
                dataset=ds,
                catchment=catchment,
                crs=clip_crs
            )

            df_precip = extract_precip_timeseries(precip=precip_crop)
            
            dfs.append(df_precip)
        
        except Exception:
            logger.exception("Failed to process ICON GRIB file: %s", file)
            continue
        
        finally:
            if ds is not None:
                ds.close()
        
        
    if not dfs:
        raise ValueError("No valid precipitation files processed.")
        
    
    # --- process dataframe ---
    df = pd.concat(dfs)
    
    df = df.sort_index()
    df = df[~df.index.duplicated(keep="last")]

    df.index.name = "timestamp"

    # cumulative -> incremental precipitation
    df["precip_mean"] = df["precip_cum_mean"].diff()

    # detect reset (new forecast cycle)
    reset_mask = df["precip_cum_mean"].diff() < 0
    df.loc[reset_mask, "precip_mean"] = df["precip_cum_mean"]


    df = (
        df
        .drop(columns=["precip_cum_mean"])
        .dropna()
    )

    return df