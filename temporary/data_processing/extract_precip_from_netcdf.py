from tqdm import tqdm
import os
from pathlib import Path
import matplotlib.pyplot as plt

import pandas as pd
import geopandas as gpd
import xarray as xr
import rioxarray



# --- Paths ---
data_root = Path(os.getcwd()) / "data"

# Hyras path
hyras_dir = data_root / "precip_hyras"
hyras_paths = [p for p in hyras_dir.rglob("*.nc") if "v6-1" in p.stem] # subset for data at 6:00 morning

# Catchment path
dtm_dir = data_root / "DTM_rlp"
basin_path = dtm_dir / "catchment_queich_siebeldingen.gpkg"


# --- Functions ---
def read_rio_and_clip(
    ds: xr.Dataset, 
    basin: gpd.GeoDataFrame
    ) -> xr.Dataset:
    
    epsg = ds.crs.epsg_code
    precip = ds["pr"]
    
    # Reproject both to same crs
    precip = precip.rio.write_crs(epsg)
    basin = basin.to_crs(epsg)
    
    # Clip precip to basin contour
    precip_clip = precip.rio.clip(
        basin.geometry,
        drop=True
    )
    
    return precip_clip    

def aggregate_to_df(data: xr.Dataset) -> pd.DataFrame:
    mean_data = data.mean(dim=["y", "x"], skipna=True)
    
    df_mean_data = mean_data.to_dataframe()
    df_mean_data = df_mean_data[["pr"]]
    
    return df_mean_data


# --- Process data ---
basin = gpd.read_file(basin_path)

dfs = []

for path in tqdm(hyras_paths):
    ds = xr.open_dataset(path)
    
    precip_clip = read_rio_and_clip(ds=ds, basin=basin)
    df_mean_precip = aggregate_to_df(data=precip_clip)
    
    dfs.append(df_mean_precip)

df_concat = pd.concat(dfs, axis="index")

df_concat.plot()
plt.show()

# --- Export data ---
output_path = hyras_dir / "precip_mean_queich_watershed.csv"
df_concat.to_csv(path_or_buf=output_path, sep=",")