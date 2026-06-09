from pathlib import Path

import pandas as pd
import geopandas as gpd

import matplotlib.pyplot as plt
import contextily as ctx

from typing import Literal

# from configs.jobs_config import (
#     UTM32N_CRS, WGS84_CRS, TEMP_STATIONS_URL, STATIONS_COL_NAMES, CATCHMENT_PATH, BUFFER_SIZE, STATIONS_WRITE_PATH
#     )
from configs import settings
from src.utils.logger import logger


def read_stations_txt(
    url: str | Path,
    colnames: list[str],
    crs: str,
    ) -> gpd.GeoDataFrame:
    
    df = pd.read_fwf(
    url,
    skiprows=2,
    header=None,
    encoding="latin1",
    )
    
    df.columns = colnames
    
    df = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(
            df["lon"],
            df["lat"]
        ),
        crs=crs
    )
    
    return df


def extract_watershed_stations(
    stations: gpd.GeoDataFrame,
    catchment: gpd.GeoDataFrame,
    utm_crs: str,
    buffer_size: int,
    ) -> gpd.GeoDataFrame:
    
    stations = stations.to_crs(crs=utm_crs)
    catchment = catchment.to_crs(crs=utm_crs)
    
    catchment_buffer_10km = catchment.buffer(buffer_size)

    stations_intersect = stations[
        stations.intersects(catchment_buffer_10km.union_all())
    ]
    
    return stations_intersect


def write_stations_to_py(
    file_path: str | Path,
    stations: gpd.GeoDataFrame,
    ) -> None:
    
    file_path = Path(file_path)
    
    if not file_path.parent.exists():
        file_path.mkdir(parents=True, exist_ok=True)
    
    stations_id = stations["stations_id"].astype(str).str.zfill(5)
    
    try:
        with open(file_path, 'w') as f:
            f.write(f"STATIONS = {list(stations_id)}")
            logger.info("Wrote %s stations in file", len(stations_id))
        
    except Exception:
        logger.exception("Failed to write stations config py")


def plot_stations(
    stations: gpd.GeoDataFrame,
    catchment: gpd.GeoDataFrame,
    ) -> None:
    catchment_web = catchment.to_crs(3857)
    stations_web = stations.to_crs(3857)

    fig, ax = plt.subplots(figsize=(12, 12))

    catchment_web.boundary.plot(ax=ax, linewidth=2)
    stations_web.plot(ax=ax, markersize=20)

    ctx.add_basemap(
        ax,
        source=ctx.providers.CartoDB.Positron
    )

    ax.set_axis_off()

    plt.show()


    
def main() -> None:
    gdf_stations = read_stations_txt(
    url=TEMP_STATIONS_URL, 
    colnames=STATIONS_COL_NAMES, 
    crs=WGS84_CRS
    )

    catchment = gpd.read_file(CATCHMENT_PATH)

    gdf_stations_intersect = extract_watershed_stations(
        stations=gdf_stations,
        catchment=catchment,
        utm_crs=UTM32N_CRS,
        buffer_size=BUFFER_SIZE,
        )
    
    write_stations_to_py(
        file_path=STATIONS_WRITE_PATH,
        stations=gdf_stations_intersect
        )
        

if __name__ == "__main__":
    main()