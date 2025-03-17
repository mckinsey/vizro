from typing import Annotated, Literal, Optional

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
        Optional[str],
        AfterValidator(validate_icon),
        Field(default="info", description="Icon name from Google Material icons library."),
    ]
    tooltip: Optional[str] = Field(
        default=None,
        description="Markdown string to create text that appears on icon hover.",
    )

    @_log_call
    def build(self):
        icon = (
            html.Span(
                self.icon,
                className="material-symbols-outlined",
                id=f"{self.id}-icon",
            )
            if self.tooltip
            else None
        )
        tooltip = (
            dbc.Tooltip(
                id=f"{self.id}-tooltip",
                children=dcc.Markdown(self.tooltip, className="markdown"),
                target=f"{self.id}-icon",
                autohide=False,
                fade=True,
            )
            if self.tooltip
            else None
        )

        return html.Div(
            id=self.id,
            children=[self.text, icon, tooltip] if self.tooltip else [self.text],
        )
