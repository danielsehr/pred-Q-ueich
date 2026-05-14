import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go


API_URL = "http://localhost:8000/forecast"

response = requests.get(API_URL)
print("response:", response)

data = response.json()


df_discharge = pd.DataFrame(data["discharge"])
df_inference = pd.DataFrame(data["inference"])

df_discharge = df_discharge.set_index(keys=["timestamp"])
df_discharge.index = pd.to_datetime(df_discharge.index)

cutoff = pd.Timestamp.now() - pd.Timedelta(days=1)

df_discharge = (
    df_discharge[df_discharge.index >= cutoff]
)

df_inference = df_inference.set_index(keys=["timestamp"])



#--- Dashboard ---
fig = go.Figure()

# historical
fig.add_trace(
    go.Scatter(
        x=df_discharge.index,
        y=df_discharge["discharge"],
        mode="lines",
        name="Observed",
    )
)

# forecast line + points
fig.add_trace(
    go.Scatter(
        x=df_inference.index,
        y=df_inference["predicted"],
        mode="lines+markers",
        name="Forecast",
        line=dict(dash="dash"),
    )
)

fig.update_layout(
    xaxis_title="Time",
    yaxis_title="Discharge",
    legend=dict(orientation="h"),
    template="plotly_white",
)

st.plotly_chart(fig, use_container_width=True)
