import requests
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go

from prepare_data import prepare_data
from configs.dashboard_config import config


# auto refresh every minute
st_autorefresh(
    interval=config["REFRESH_INTERVAL"],
    key="dashboard_refresh",
)


# --- GET request ---
try:
    response = requests.get(config["API_URL"], timeout=10)
    response.raise_for_status()

    data = response.json()

except requests.RequestException as e:
    st.error(f"API unavailable: {e}")
    st.stop()


# --- Prepare data for plotting ---
df_discharge = pd.DataFrame(data["discharge"])
df_inference = pd.DataFrame(data["inference"])

df_discharge = prepare_data(df_discharge, days=1)
df_inference = prepare_data(df_inference, days=1)


#--- Dashboard ---
fig = go.Figure()

# historical
fig.add_trace(
    go.Scatter(
        x=df_discharge.index,
        y=df_discharge["discharge"],
        mode="lines+markers",
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

st.plotly_chart(fig)
