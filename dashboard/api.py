import requests
import streamlit as st

from configs.dashboard_config import API_URL


@st.cache_data(ttl=600)
def fetch_dashboard_data() -> dict:
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:
        st.error(f"API unavailable: {e}")
        st.stop()
        
    