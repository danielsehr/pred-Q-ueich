![Status](https://img.shields.io/badge/status-active%20development-orange)

# Pred-Q-ueich
Overview

An end-to-end hydrological forecasting system for predicting river discharge in the Queich catchment.

This project continuously ingests environmental observations and weather forecast data from DWD, processes and stores time-series data, performs machine learning inference, and serves results through an API and interactive dashboard.

<br>

## Usage

### 1.  Open directory
````bash
cd PythonProjects/discharge_queich
````
<br>


### 2. Start uvicorn server

On windows:
````bash
uv run uvicorn discharge_queich.api.main:app --reload --host 127.0.0.1 --port 8000
````

On raspi:
````bash
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
````
<br>


### 3. Run streamlit
````bash
uv run streamlit run src/discharge_queich/dashboard/app.py
````

<br> <br>


### 4. Run scheduler
````bash
python -m scheduler.scheduler
````

<br> <br>
