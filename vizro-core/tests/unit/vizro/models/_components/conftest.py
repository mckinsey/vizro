"""Fixtures to be used in components related tests."""
import plotly.graph_objects as go
import pytest
from dash import dcc

import vizro.plotly.express as px
from vizro.models._components.graph import create_empty_fig


@pytest.fixture
def standard_px_chart_with_str_dataframe():
    return px.scatter(
        data_frame="gapminder",
        x="gdpPercap",
        y="lifeExp",
        size="pop",
        color="continent",
        hover_name="country",
        size_max=60,
    )


@pytest.fixture
def expected_empty_chart():
    figure = go.Figure()
    figure.add_trace(go.Scatter(x=[None], y=[None], showlegend=False, hoverinfo="none"))
    figure.update_layout(
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[{"text": "NO DATA", "showarrow": False, "font": {"size": 16}}],
    )
    return figure


@pytest.fixture
def expected_graph():
    return dcc.Loading(
        dcc.Graph(
            id="text_graph",
            figure=create_empty_fig("NO DATA"),
            config={
                "autosizable": True,
                "frameMargins": 0,
                "responsive": True,
            },
            className="chart_container",
        ),
        color="grey",
        parent_className="chart_container",
    )
