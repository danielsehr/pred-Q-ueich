# Pred-Q-ueich

## Usage

### 1. Activate Environment
````bash
conda activate queich_env
````
<br>


### 2.  Open directory
````bash
cd PythonProjects/abfluss_queich
````
<br>


### 3. Start uvicorn server

On windows:
````bash
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
````

On raspi:
````bash
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
````
<br>


### 4. Run streamlit
````bash
python -m streamlit run dashboard/app.py
````

<br> <br>


### 5. Run scheduler
````bash
python -m scheduler.scheduler
````

<br> <br>

## Project Architecture

### Folder Structure
````
project/
│
├── api/
│   ├── main.py
│   └── modules.py
│
├── architecture/
│   └── Pre-Q-ueich.drawio
│
├── configs/
│   ├── __init__.py
│   ├── dashboard_config.py
│   ├── database_config.py
│   ├── jobs_config.py
│   ├── model_config.py
│   └── scheduler_config.py
│
├── dashboard/
│   ├── __init__.py
│   ├── app.py
│   └── prepare_data.py
│
├── database/
│   ├── __init__.py
│   ├── db.py
│   ├── init_db.py
│   ├── models.py
│   └── queries.py
│
├── jobs/
│   ├── __init__.py
│   ├── discharge/
│   │   ├── preprocessing/
│   │   ├── fetch_discharge.py
│   │   └── ingest_discharge.py
│   │   
│   ├── icon/
│   │   ├── decompress_icon.py
│   │   ├── fetch_icon.py
│   │   ├── ingest_icon.py
│   │   └── process_icon.py
│   │   
│   ├── inference/
│   │   └── ingest_ingerence.py
│   │   
│   └── radolan/
│   │   ├── decompress_radolan.py
│   │   ├── fetch_radolan.py
│   │   ├── ingest_radolan.py
│   │   └── process_radolan.py
│
├── model/
│   ├── __init__.py
│   ├── build_model.py
│   ├── create_training_dataset.ipynb
│   ├── dataset.py
│   ├── evaluate_model.py
│   ├── evaluation.py
│   ├── features.py
│   ├── inference.py
│   ├── test_features.py
│   └── train_model.py
│
├── models/
│
└── scheduler/
│   └── scheduler.py
│
├── utils/
│   └── logger.py
│
├── README.md
├── __init__.py
└── temp.ipynb
````



