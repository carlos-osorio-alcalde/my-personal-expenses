import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from dashboard.styles import Styles


def time_series_plot(df: pd.DataFrame) -> px.line:
    """
    This function creates a time series plot

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame of expenses

    Returns
    -------
    px.line
        The time series plot
    """
    fig_time_series = px.line(
        df,
        x="date",
        y="amount_moving_average",
        title="",
        template="plotly_white",
    )

    # Update the layout
    fig_time_series.update_layout(
        xaxis_title="Date",
        yaxis_title="Expenses moving average",
        font=dict(size=18),
        margin=dict(l=0, r=0, t=50, b=0),
    )

    # Add a modern style to the plot
    fig_time_series.update_traces(
        line=dict(width=3, color=Styles._THEME_COLOR),
        marker=dict(size=10, color=Styles._THEME_COLOR),
    )

    # Show the plot
    return fig_time_series
