from typing import Literal, Optional

import dash_bootstrap_components as dbc
from dash import dcc, get_relative_path, html
from pydantic import Field

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call


class Card(VizroBaseModel):
    """Creates a card utilizing `dcc.Markdown` as title and text component.

    Args:
        type (Literal["card"]): Defaults to `"card"`.
        text (str): Markdown string to create card title/text that should adhere to the CommonMark Spec.
        href (Optional[str]): URL (relative or absolute) to navigate to. If not provided the Card serves as a text card
            only. Defaults to None.
    """

    type: Literal["card"] = "card"
    text: str = Field(
        ..., description="Markdown string to create card title/text that should adhere to the CommonMark Spec."
    )
    href: Optional[str] = Field(
        None,
        description="URL (relative or absolute) to navigate to. If not provided the Card serves as a text card only.",
    )

    @_log_call
    def build(self):
        text = dcc.Markdown(self.text, className="card_text", dangerously_allow_html=False, id=self.id)
        button = (
            html.Div(
                dbc.Button(
                    href=get_relative_path(self.href) if self.href.startswith("/") else self.href,
                    className="card_button",
                ),
                className="button_container",
            )
            if self.href
            else html.Div(hidden=True)
        )
        card_container = "nav_card_container" if self.href else "card_container"

        return html.Div([text, button], className=card_container, id=f"{self.id}_outer")
