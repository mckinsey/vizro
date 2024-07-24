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
    # TODO: remove text, make code non-optional
    text: str = ""
    code: str = ""
    language: str = ""

    def build(self):
        """Returns the code clipboard component inside an accordion."""
        markdown_code = self.text or "\n".join([f"```{self.language}", self.code, "```"])
        return dbc.Accordion(
            [
                dbc.AccordionItem(
                    html.Div(
                        [
                            html.H3(self.title),
                            dcc.Markdown(markdown_code, id=self.id),
                            dcc.Clipboard(target_id=self.id, className="code-clipboard"),
                        ],
                        className="code-clipboard-container",
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
    """Creates a custom butterfly chart using Plotly's go.Figure.

    A butterfly chart is a type of bar chart where two sets of bars are displayed back-to-back, often used to compare
    two sets of data.

    Args:
        data_frame (pd.DataFrame): The data source for the chart.
        x1 (str): The name of the column in the data frame for the first set of bars (negative values).
        x2 (str): The name of the column in the data frame for the second set of bars (positive values).
        y (str): The name of the column in the data frame for the y-axis (categories).

    Returns:
        go.Figure: A Plotly Figure object representing the butterfly chart.

    """
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


# TODO: think about where this goes
@capture("graph")
def sankey(data_frame: pd.DataFrame, source: str, target: str, value: str, labels: List[str]) -> go.Figure:
    """Creates a custom sankey chart using Plotly's `go.Sankey`.

    A Sankey chart is a type of flow diagram where the width of the arrows is proportional to the flow rate.
    It is used to visualize the flow of resources or data between different stages or categories.

    Args:
        data_frame (pd.DataFrame): The data source for the chart.
        source (str): The name of the column in the data frame for the source nodes.
        target (str): The name of the column in the data frame for the target nodes.
        value (str): The name of the column in the data frame for the values representing the flow between nodes.
        labels (List[str]): A list of labels for the nodes.

    Returns:
        go.Figure: A Plotly Figure object representing the Sankey chart.

    For detailed information on additional parameters and customization, refer to the Plotly documentation:
    https://plotly.com/python/reference/sankey/

    """
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


vm.Container.add_type("components", FlexContainer)
vm.Container.add_type("components", Markdown)
vm.Page.add_type("components", CodeClipboard)
