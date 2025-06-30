"""Custom charts for the app."""

import pandas as pd
import plotly.graph_objects as go
from vizro.models.types import capture


@capture("graph")
def custom_bar(data_frame: pd.DataFrame, x: str, y: str) -> go.Figure:
    """Custom bar chart."""
    return go.Figure(data=[go.Bar(x=data_frame[x], y=data_frame[y])])
