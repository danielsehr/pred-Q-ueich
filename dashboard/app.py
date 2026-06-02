import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go

from configs import settings

from dashboard.api import fetch_dashboard_data
from dashboard.prepare_data import prepare_datasets
from dashboard.plotting.layout import create_dashboard_layout


st.set_page_config(layout="wide")

st_autorefresh(
    interval=settings.dashboard.refresh_interval,
    key="dashboard_refresh",
)


data = fetch_dashboard_data()

datasets = prepare_datasets(
    data=data,
    days=settings.dashboard.default_dashboard_days
    )

fig = create_dashboard_layout(data=datasets)


config = {
    "scrollZoom": True
}

st.plotly_chart(fig, width="stretch", config=config)
