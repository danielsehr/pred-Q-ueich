from plotly.graph_objects import Figure
from plotly.subplots import make_subplots
from dashboard.plotting.discharge import add_discharge_traces, add_inference_traces
from dashboard.plotting.precipitation import add_precip_obs_traces, add_precip_pred_traces
from dashboard.plotting.utils import add_empty_bars


def configure_layout(fig: Figure) -> Figure:
    
    fig.update_layout(
        title=dict(
            text="Queich Discharge Forecast", 
            x=0.5, xanchor="center", 
            font=dict(
                size=30
                )
            ),
        xaxis_title="Time",
        
        legend=dict(orientation="h"),

        hovermode="x unified",
        dragmode="pan",
        
        template="plotly_white",
        height=850
    )
    
    # --- Update y axes ---
    fig.update_yaxes(
        title_text="Precipitation [mm]", row=1, col=1,
        scaleanchor=None
        )
    
    fig.update_yaxes(
        title_text="Discharge [m³/s]", row=2, col=1
        )
    
    # --- Update x axes ---
    fig.update_xaxes(
        title_text="Time", row=2, col=1,
        rangeslider_visible=True
        )
    
    return fig



def create_dashboard_layout(data: dict):
    
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.5, 0.5],
    )
    
    
    fig = add_precip_obs_traces(fig=fig, precip_obs=data["precip_hourly_obs"])
    
    fig = add_precip_pred_traces(fig=fig, precip_pred=data["precip_pred"])
    
    fig = add_discharge_traces(fig=fig, discharge=data["discharge"])

    fig = add_inference_traces(fig=fig, inference=data["inference"])

    
    fig = configure_layout(fig)
    
    return fig