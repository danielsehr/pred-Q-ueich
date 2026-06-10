import plotly.graph_objects as go
from plotly.graph_objects import Figure
import pandas as pd


def add_discharge_traces(
    fig: Figure,
    discharge: pd.DataFrame,
    ) -> Figure:
    
    fig.add_trace(
        go.Scatter(
        x=discharge.index,
        y=discharge["discharge"],
        mode="lines+markers",
        name="Observed Discharge",
        ),
    row=2,
    col=1,
    )
    
    return fig


def add_inference_traces(
    fig: Figure,
    inference: pd.DataFrame,
    ) -> Figure:
    
    fig.add_trace(
        go.Scatter(
            x=inference.index,
            y=inference["predicted"],
            mode="lines+markers",
            name="Observed Discharge",
        ),
        row=2,
        col=1,
    )
    
    return fig


