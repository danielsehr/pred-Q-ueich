import requests
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from dashboard.prepare_data import prepare_data
from configs.dashboard_config import API_URL, REFRESH_INTERVAL


# auto refresh every minute
st_autorefresh(
    interval=REFRESH_INTERVAL,
    key="dashboard_refresh",
)


# --- GET request ---
try:
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()

    data = response.json()

except requests.RequestException as e:
    st.error(f"API unavailable: {e}")
    st.stop()


# --- Prepare data for plotting ---
df_discharge = pd.DataFrame(data["discharge"])
df_inference = pd.DataFrame(data["inference"])
df_precip_obs = pd.DataFrame(data["precip_obs"])
df_precip_pred = pd.DataFrame(data["precip_pred"])

days=14

df_discharge = prepare_data(df_discharge, days=days)
df_inference = prepare_data(df_inference, days=days)
df_precip_obs = prepare_data(df_precip_obs, days=days)
df_precip_pred = prepare_data(df_precip_pred, days=days)


#--- DASHBOARD ---
fig  = make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.1,
    row_heights=[0.5, 0.5],
)

# --- PRECIPITATION ---
def add_empty_bars(
    df: pd.Series,
    epsilon: float,
    ):
    
    plot_vals = df.mask(df == 0, epsilon)
    
    return plot_vals


# Observed Precipitation
obs_precip_vals = df_precip_obs["precip_mean"]
obs_precip_plot_vals = add_empty_bars(
    df=obs_precip_vals, 
    epsilon=0.001
    )

fig.add_trace(
    go.Bar(
        x=df_precip_obs.index,
        y=obs_precip_plot_vals,
        customdata=obs_precip_vals,
        name="Observed Precipitation",
        opacity=0.7,
        hovertemplate=(
            "Time: %{x}<br>"
            "Obs. Precipitation: %{customdata} mm"
            "<extra></extra>"
        ),
    ),
    row=1,
    col=1,
)

# Predicted Precipitation
pred_precip_vals = df_precip_pred["precip_mean"]
pred_precip_plot_vals = add_empty_bars(
    df=pred_precip_vals, 
    epsilon=0.001
    )


fig.add_trace(
    go.Bar(
        x=df_precip_pred.index,
        y=pred_precip_plot_vals,
        customdata=pred_precip_vals,
        name="Forecast Precipitation",
        opacity=0.7,
        hovertemplate=(
            "Time: %{x}<br>"
            "Pred. Precipitation: %{customdata} mm"
            "<extra></extra>"
        ),
    ),
    row=1,
    col=1,
)

# --- DISCHARGE ---
# historical
fig.add_trace(
    go.Scatter(
        x=df_discharge.index,
        y=df_discharge["discharge"],
        mode="lines+markers",
        name="Observed Discharge",
    ),
    row=2,
    col=1,
)

# forecast line + points
fig.add_trace(
    go.Scatter(
        x=df_inference.index,
        y=df_inference["predicted"],
        mode="lines+markers",
        name="Forecast Discharge",
        line=dict(dash="dash"),
    ), 
    row=2,
    col=1,
)

st.set_page_config(layout="wide")

fig.update_layout(
    title=dict(
        text="Queich Discharge Forecast", 
        x=0.5, xanchor="center", 
        font=dict(
            size=30
            )
        ),
    xaxis_title="Time",
    yaxis_title="Discharge",
    legend=dict(orientation="h"),
    template="plotly_white",
    height=850
)

fig.update_yaxes(title_text="Precipitation [mm]", row=1, col=1)
fig.update_yaxes(title_text="Discharge [m³/s]", row=2, col=1)
fig.update_xaxes(title_text="Time", row=2, col=1)

st.plotly_chart(fig, width="stretch")
