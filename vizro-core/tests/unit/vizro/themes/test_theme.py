"""Tests for templates."""
import plotly.express as px
from plotly.graph_objs.layout._template import Template

from vizro._themes._color_values import COLORS


def test_template(template):
    assert isinstance(template, Template)


def test_color_palette_applied(chart_data, template):
    fig_1 = px.scatter(chart_data, x="x", y="y", color="y")  # continuous column for color
    fig_2 = px.scatter(chart_data, x="x", y="y", color="x")  # discrete column for color

    marker_colors = [fig_2.data[i].marker.color for i in range(len(fig_2.data))]
    assert fig_1.layout.coloraxis.colorscale == template.layout.colorscale.sequential
    assert marker_colors == COLORS["DISCRETE_10"][: len(marker_colors)]
