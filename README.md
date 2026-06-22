![Status](https://img.shields.io/badge/status-active%20development-orange)

# Pred-Q-ueich

## Overview

An end-to-end hydrological forecasting system for predicting river discharge in the Queich catchment.

This project continuously ingests environmental observations and weather forecast data from DWD, processes and stores time-series data, performs machine learning inference, and serves results through an API and interactive dashboard.

<br>

## Project Structure
```
.
├── src/discharge_queich
│   ├── api/
│   ├── architecture
│   ├── configs
│   ├── dashboard/
│   ├── database/
│   ├── jobs/
│   ├── model/
│   ├── models/
│   ├── notebooks/
│   ├── scheduler/
│   ├── utils/
│   └── __init__.py
│ 
├── data/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── README.md
└── uv.lock
```

<br>

## Usage

### Docker Setup
Make sure you have installed:

- Docker Desktop (Windows/macOS/Linux)
- Docker Compose v2+

#### 1. Build Container
```bash
docker compose build
```

#### 2. Start services
```bash
docker compose up
```

#### 3. Open dashboard
```bash
http://localhost:8501/
```

#### 4. Stop all services
```bash
docker compose down
```
<br>

## Local Developement Setup
### 1.  Open directory
````bash
cd ./discharge_queich
````
<br>


### 2. Start uvicorn server

On windows:
````bash
uv run uvicorn discharge_queich.api.main:app --reload --host 127.0.0.1 --port 8000
````
<br>


### 3. Run streamlit
````bash
uv run streamlit run src/discharge_queich/dashboard/app.py
````

<br>


### 4. Run scheduler
````bash
python -m scheduler.scheduler
````

<br> <br>
