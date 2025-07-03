"""Collection of custom charts."""

import pandas as pd
import plotly.graph_objects as go
from vizro.models.types import capture


@capture("graph")
def custom_scatter(data_frame: pd.DataFrame, x: str, y: str):
    """Custom scatter plot."""
    return go.Figure(data=[go.Scatter(x=data_frame[x], y=data_frame[y])])
