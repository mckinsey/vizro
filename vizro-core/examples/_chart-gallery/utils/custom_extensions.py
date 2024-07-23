"""Contains custom components and charts used inside the dashboard."""

from typing import List, Literal

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm
from dash import dcc, html
from vizro.models.types import capture

try:
    from pydantic.v1 import Field
except ImportError:  # pragma: no cov
    from pydantic import Field


class CodeClipboard(vm.VizroBaseModel):
    """Contains code snippet with a copy to clipboard button."""

    type: Literal["code_clipboard"] = "code_clipboard"
    title: str = "Code"
    text: str

    def build(self):
        """Returns the code clipboard component inside an accordion."""
        return dbc.Accordion(
            [
                dbc.AccordionItem(
                    html.Div(
                        [
                            html.H3(self.title),
                            dcc.Markdown(self.text, id=self.id),
                            dcc.Clipboard(target_id=self.id, className="code-clipboard"),
                        ],
                        className="code-clipboard-container"
                    ),
                    title="SHOW CODE",
                )
            ],
            start_collapsed=False,
        )


class Markdown(vm.VizroBaseModel):
    """Markdown component."""

    type: Literal["markdown"] = "markdown"
    text: str = Field(
        ..., description="Markdown string to create card title/text that should adhere to the CommonMark Spec."
    )
    classname: str = ""

    def build(self):
        """Returns a markdown component with an optional classname."""
        return dcc.Markdown(id=self.id, children=self.text, dangerously_allow_html=False, className=self.classname)


class FlexContainer(vm.Container):
    """Custom flex `Container`."""

    type: Literal["flex_container"] = "flex_container"

    def build(self):
        """Returns a flex container."""
        return html.Div(
            id=self.id, children=[component.build() for component in self.components], className="flex-container"
        )


@capture("graph")
def butterfly(data_frame: pd.DataFrame, x1: str, x2: str, y: str) -> go.Figure:
    """Creates a custom butterfly chart based on a go.Figure."""
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=-data_frame[x1].values,
            y=data_frame[y],
            orientation="h",
            name=x1,
        )
    )
    fig.add_trace(
        go.Bar(
            x=data_frame[x2],
            y=data_frame[y],
            orientation="h",
            name=x2,
        )
    )
    fig.update_layout(barmode="relative")
    return fig


@capture("graph")
def sankey(data_frame: pd.DataFrame, source: str, target: str, value: str, labels: List[str]) -> go.Figure:
    """Creates a custom sankey chart based on a go.Figure."""
    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(  # noqa: C408
                    pad=16,
                    thickness=16,
                    label=labels,
                ),
                link=dict(  # noqa: C408
                    source=data_frame[source],
                    target=data_frame[target],
                    value=data_frame[value],
                    label=labels,
                    color="rgba(205, 209, 228, 0.4)",
                ),
            )
        ]
    )
    fig.update_layout(barmode="relative")
    return fig
