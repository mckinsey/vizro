from typing import Literal

import dash_bootstrap_components as dbc
from dash import dcc, html
from pydantic import Field

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call


class Title(VizroBaseModel):
    """Creates a title component.

    Args:
        type (Literal["title"]): Defaults to `"title"`.
        title (str): Dashboard title to appear on every page on top left-side. Defaults to `""`.
        icon (bool): Boolean to add information icon to dashboard title. Defaults to `""`.
        tooltip_text (str): Markdown string to create  text that appears on icon hover.

    """

    type: Literal["title"] = "title"
    title: str = Field(default="", description="Dashboard title to appear on every page on top left-side.")
    icon: bool = False
    tooltip_text: str = Field(description="Markdown string to create card text that appears on icon hover.")

    @_log_call
    def build(self):
        tooltip_text = dcc.Markdown(self.tooltip_text, dangerously_allow_html=True, id="dashboard-title-markdown")

        dashboard_title = (
            html.H2(id="dashboard-title-title", children=self.title)
            if self.title
            else html.H2(id="dashboard-title-title", hidden=True)
        )
        tooltip = dbc.Tooltip(
            children=tooltip_text,
            placement="right",
            target=f"{self.id}-icon",
        )
        complete_title = html.Div(
            id="dashboard-title",
            children=[
                dashboard_title,
                html.Span("info", className="material-symbols-outlined", id=f"{self.id}-icon"),
                html.Div(tooltip, style={"whiteSpace": "normal"}),
            ],
        )
        return complete_title
