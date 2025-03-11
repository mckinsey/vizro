from typing import Annotated, Literal

import dash_bootstrap_components as dbc
from dash import dcc, html
from pydantic import AfterValidator, Field

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call, validate_icon


class Title(VizroBaseModel):
    """Creates a title component.

    Args:
        type (Literal["title"]): Defaults to `"title"`.
        text (str): Dashboard title to appear on every page on top left-side.
        icon (str): Icon name from [Google Material icons library](https://fonts.google.com/icons).
            Defaults to `"info"`.
        tooltip (str): Markdown string to create text that appears on icon hover.

    """

    type: Literal["title"] = "title"
    text: str = Field(description="Dashboard title to appear on every page on top left-side.")
    icon: Annotated[
        str,
        AfterValidator(validate_icon),
        Field(default="info", description="Icon name from Google Material icons library."),
    ]
    tooltip: str = Field(description="Markdown string to create text that appears on icon hover.")

    @_log_call
    def build(self):
        return html.Div(
            id="dashboard-title",
            children=[
                html.H2(id="dashboard-title-text", children=self.text),
                html.Span(self.icon, className="material-symbols-outlined", id=f"{self.id}-icon"),
                dbc.Tooltip(
                    id=f"{self.id}-tooltip",
                    children=dcc.Markdown(self.tooltip, dangerously_allow_html=True, id="dashboard-title-markdown"),
                    placement="left",
                    target=f"{self.id}-icon",
                ),
            ],
        )
