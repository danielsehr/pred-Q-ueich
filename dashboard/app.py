import requests
import pandas as pd
import streamlit as st


API_URL = "http://localhost:9000/forecast"

response = requests.get(API_URL)

data = response.json()

df = pd.DataFrame(data)

st.title("Queich Forecast Dashboard")

st.line_chart(df[["observed", "predicted"]])