"""Collection of custom charts."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from vizro.models.types import capture


@capture("graph")
def custom_scatter(data_frame: pd.DataFrame, x: str, y: str):
    """Custom scatter plot."""
    return go.Figure(data=[go.Scatter(x=data_frame[x], y=data_frame[y])])


@capture("graph")
def create_bubble(data_frame):
    fig = px.scatter_geo(
        data_frame,
        locations="State_Code",
        locationmode="USA-states",
        size="Sales",
        hover_name="State",
        hover_data={"Sales": ":$,.0f", "State_Code": False},
        size_max=40,
        title="Sales | By State",
        scope="usa",
    )

    fig.update_layout(
        title={
            "text": "Sales | By State",
            "x": 0.5,
            "xanchor": "center",
        },
        geo=dict(
            showland=True,
            landcolor="#e8ecf0",
            showlakes=True,
            lakecolor="#ffffff",
            projection_type="albers usa",
            showframe=True,
            showcoastlines=True,
            showsubunits=True,
        ),
    )

    return fig
