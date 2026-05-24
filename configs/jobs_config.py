# --- DISCHARGE ---
# --- fetch_discharge.py --- 
DISCHARGE_URL = (
    "https://geodaten-wasser.rlp-umwelt.de/api/data/messstellen_wasserstand_abflusswerte_30?w=messstellennummer=2377050700"
)

DISCHARGE_HEADERS  = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://geodaten-wasser.rlp-umwelt.de/",
}

# --- ICON PRECIP FORECAST ---
# --- fetch_icon.py ---
ICON_URL = "https://opendata.dwd.de/weather/nwp/icon-d2/grib/00/tot_prec/"

ICON_OUTPUT_DIR = "data/forecast_precip/icon_d2/compressed"


# --- decompress.py ---
DECOMPRESSED_DIR = "data/forecast_precip/icon_d2/decompressed"


# --- process.py ---
CATCHMENT_PATH = "data/catchment/catchment_queich_siebeldingen.gpkg"

CLIP_CRS = "EPSG: 4326"


# --- RADOLAN PRECIP OBSERVATION ---
RADOLAN_URL = "https://opendata.dwd.de/climate_environment/CDC/grids_germany/5_minutes/radolan/recent/"

ICON_OUTPUT_DIR = "data/observed_precip/radolan/compressed"

RADOLAN_DECOMPRESSED_DIR = "data/observed_precip/radolan/decompressed"