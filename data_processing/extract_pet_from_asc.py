from tqdm import tqdm
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import rasterio
from rasterio.windows import Window
from rasterio.plot import plotting_extent
from rasterio.transform import rowcol
from pyproj import Transformer


# Locate all .asc files
root = Path("C:/Users/Administrator/PythonProjects/abfluss_queich/data")

keywords = ["data", "evapo"]
pet_paths = [
    f for f in root.rglob("*.asc") 
    if any(k in f.name for k in keywords)
    ]

print(f"Found {len(pet_paths)} asc files")



# --- Transform coordinates to row/col index in asc raster ---

# Hardcoded location in ESPG 4326 (WGS84)
locations_4326 = {
    "Bad Bergzabern": (7.9967, 49.1070),
    "Dahn": (7.7803, 49.1421),
    "Pirmasens": (7.5879, 49.1912),
}

# Create transformer object from EPSG4326 to EPSG 31467, Gauss-Krueger Zone 3
transformer = Transformer.from_crs("EPSG:4326", "EPSG:31467", always_xy=True)

# Transform locations to EPSG 31467
locations_31467 = {}

for key, (lon, lat) in locations_4326.items():
    x, y = transformer.transform(lon, lat)
    
    locations_31467[key] = (x, y)


# Extract transform from one asc file to get pixel position
with rasterio.open(pet_paths[0]) as src:
    transform = src.window_transform(window)

# Get pixel position as lut
pixel_lut = {
    loc: rowcol(transform, x, y)
    for loc, (x, y) in locations_31467.items()
}



# --- Extract PET ---

# Window to read
window = Window(
    col_off=100, row_off=600,
    width=100, height=100
)


asc_dict = {}

# pet_paths_sub = pet_paths[:20]
for path in tqdm(pet_paths, total=len(pet_paths)):
   
    # Extract date from filename
    datestring = path.stem.split("_")[-1]
    timestamp = pd.to_datetime(datestring, format="%Y%m%d")
    
    # Read data from asc file
    with rasterio.open(path) as src:
        data = src.read(1, window=window)

        # nodata
        nodata = src.nodata
        data = np.where(data == nodata, np.nan, data)

    
    # Extract PET from 3 location
    pet_dict = {}
    
    for location, (row, col) in pixel_lut.items():
        pet = data[row, col]

        pet_dict[location] = pet
    
    # Add pet dict to asc dict
    asc_dict[timestamp] = pet_dict


# Create dataframe and export as CSV
pet_dataframe = pd.DataFrame.from_dict(asc_dict, orient="index")

output_dir = root / "pet"
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "all_pet.csv"

pet_dataframe.to_csv(output_path, sep=",", header=True, index=True)