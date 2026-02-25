"""Test vizro_dash_components works inside a Vizro dashboard as a custom Dash component."""

import pandas as pd
import vizro.models as vm
import vizro_dash_components as vdc
from dash import html
from vizro import Vizro
from vizro.models.types import capture

df = pd.DataFrame({"x": [1]})


@capture("figure")
def custom_markdown_figure(data_frame: pd.DataFrame) -> html.Div:
    return html.Div(
        vdc.Markdown(
            "# Hello from vdc\n\n```python\nprint('hello')\n```",
            id="vdc-markdown",
        )
    )


def test_vizro_dashboard_with_vdc_markdown(dash_duo):
    """vdc.Markdown used as a custom Dash component inside a Vizro dashboard renders without errors."""
    page = vm.Page(
        title="Test page",
        components=[vm.Figure(figure=custom_markdown_figure(data_frame=df))],
    )
    dashboard = vm.Dashboard(pages=[page])
    app = Vizro().build(dashboard).dash
    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#vdc-markdown h1", "Hello from vdc")
    assert dash_duo.get_logs() == []
