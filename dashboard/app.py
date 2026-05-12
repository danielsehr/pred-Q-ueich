import requests
import pandas as pd
import streamlit as st


API_URL = "http://localhost:8000/forecast"

response = requests.get(API_URL)

data = response.json()

df = pd.DataFrame(data)
df = df.set_index(keys=["timestamp"])
print(df)


#--- Dashboard ---
st.title("Queich Forecast Dashboard")
st.line_chart(
    data=df[["discharge"]],
    )
