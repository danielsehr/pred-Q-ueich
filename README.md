# Pred-Q-ueich

## Usage

### 1. Start uvicorn server

On windows:
````bash
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
````

On raspi:
````bash
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
````
<br>


### 2. Run streamlit
````bash
python -m streamlit run dashboard/app.py
````

<br> <br>


## System Architecture

### Overview
````
pred-Q-ueich/
│
├── api/
│   └── main.py
│
├── dashboard/
│   └── app.py
│
├── database/
│   ├── db.py
│   ├── models.py
│   └── init_db.py
│
├── jobs/
│   └── run_forecast.py
│
├── queich.db
│
└── environment.yml
````

---

### High-Level Data Flow

```text
jobs/
    ↓
database/
    ↓
api/
    ↓
dashboard/


