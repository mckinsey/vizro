"""Tests for templates."""
import numpy as np
import pandas as pd
import plotly.express as px
import pytest
from plotly.graph_objs.layout._template import Template

import vizro._themes as themes
from vizro._themes._color_values import COLORS


@pytest.fixture
def template():
    """Fixture for template."""
    return np.random.choice([themes.dark, themes.light], 1)[0]


@pytest.fixture
def chart_data():
    """Fixture for chart data."""
    data_points = np.random.randint(0, 100, 1, dtype=int)
    data = pd.DataFrame(
        {
            "x": np.random.choice(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"], data_points),
            "y": np.random.normal(0, 200, data_points),
        }
    )
    return data


def test_template(template):
    assert isinstance(template, Template)


def test_color_palette_applied(chart_data, template):
    fig_1 = px.scatter(chart_data, x="x", y="y", color="y")  # continuous column for color
    fig_2 = px.scatter(chart_data, x="x", y="y", color="x")  # discrete column for color

    marker_colors = [fig_2.data[i].marker.color for i in range(len(fig_2.data))]
    assert fig_1.layout.coloraxis.colorscale == template.layout.colorscale.sequential
    assert marker_colors == COLORS["DISCRETE_10"][: len(marker_colors)]
