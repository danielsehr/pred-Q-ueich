from tqdm import tqdm
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import tarfile


#--- Scrap tgz files from DWD ---

# URL of PET raster data from DWD
url = "https://opendata.dwd.de/climate_environment/CDC/grids_germany/daily/evapo_p/"  # <-- change this

# Create download folder
root = Path("./data")
output_dir = root / "pet_germany"

# Get webpage
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Find all links and filter
links = soup.find_all("a") 

for link in tqdm(links):
    href = link.get("href")
    
    if href and href.endswith(".tgz"):
        file_url = urljoin(url, href)
        tgz_dir = output_dir / "tgz_files" 
        tgz_dir.mkdir(parents=True, exist_ok=True)
        
        tgz_path = tgz_dir / href
        
        # print(f"Downloading: {file_url}")
        
        with requests.get(file_url, stream=True) as r:
            r.raise_for_status()
            with open(tgz_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

print("Done downloading tgz files!")



#--- Extraxt tgz files ---

# Set file paths for unpacking
root = Path("C:/Users/Administrator/PythonProjects/abfluss_queich/data/pet_germany")
input_dir = root / "tgz_files"
output_dir = root / "extracted"
output_dir.mkdir(parents=True, exist_ok=True)


# Extract all files
total = len([p for p in input_dir.glob("*.tgz")])

for path in tqdm(input_dir.glob("*.tgz"), total = total):
    with tarfile.open(path) as tar:
        output_path = output_dir / path.stem
        tar.extractall(path=output_path)
print("Done extracting tgz files!")