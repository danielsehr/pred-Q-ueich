import plotly.graph_objects as go
from plotly.graph_objects import Figure
import pandas as pd

from src.dashboard.plotting.utils import add_empty_bars


def add_precip_obs_traces(
    fig: Figure,
    precip_obs: pd.DataFrame,
    ) -> Figure:
    
    precip_obs_plot = add_empty_bars(df=precip_obs)
    
    fig.add_trace(
        go.Bar(
            x=precip_obs.index,
            y=precip_obs_plot["precip_mean"],
            customdata=precip_obs["precip_mean"],
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
    
    return fig
    
    
def add_precip_pred_traces(
    fig,
    precip_pred: pd.DataFrame,
    ):
    
    precip_pred_plot = add_empty_bars(df=precip_pred)
    
    fig.add_trace(
        go.Bar(
            x=precip_pred.index,
            y=precip_pred_plot["precip_mean"],
            customdata=precip_pred["precip_mean"],
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
    
    return fig