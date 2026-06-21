# Pred-Q-ueich

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
