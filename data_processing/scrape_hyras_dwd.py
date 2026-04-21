from tqdm import tqdm
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin


#--- Scrap hyras precip files from DWD ---

# URL of PET raster data from DWD
url = "https://opendata.dwd.de/climate_environment/CDC/grids_germany/daily/hyras_de/precipitation/"

# Create download folder
root = Path("./data")
output_dir = root / "precip_hyras"

# Get webpage
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Find all links and filter
links = soup.find_all("a") 

# Years to scrape
start = 2000
end = 2026
years = [year for year in range(start, end+1, 1)]


for link in tqdm(links):
    href = link.get("href")
    
    if href and href.endswith(".nc"):
        if any(str(year) in href for year in years):
            file_url = urljoin(url, href)
            output_path = output_dir / href
            
            with requests.get(file_url, stream=True) as r:
            
                r.raise_for_status()
            
                with open(output_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

print("Done downloading files!")