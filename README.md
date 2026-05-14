# Pred-Q-ueich

## Usage

### 1. Activate Environment
````bash
conda activate queich_env
````


### 2. Start uvicorn server

On windows:
````bash
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
````

On raspi:
````bash
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
````
<br>


### 3. Run streamlit
````bash
python -m streamlit run dashboard/app.py
````

<br> <br>


## System Architecture

### Overview
````

````



