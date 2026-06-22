import requests
import streamlit as st

from discharge_queich.configs import settings


@st.cache_data(ttl=600)
def fetch_dashboard_data() -> dict:
    
    try:
        response = requests.get(
            url=settings.dashboard.api_url,
            timeout=10
            )
        
        response.raise_for_status()

        return response.json()


    except requests.RequestException as e:
        st.error(f"API unavailable: {e}")
        st.stop()
        
    