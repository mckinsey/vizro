from typing import Literal

import dash_bootstrap_components as dbc
from dash import dcc, get_relative_path, html

try:
    from pydantic.v1 import Field, validator
except ImportError:  # pragma: no cov
    from pydantic import Field, validator

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _clean_url, _is_relative_url, _log_call


class Card(VizroBaseModel):
    """Creates a card utilizing `dcc.Markdown` as title and text component.

    Args:
        type (Literal["card"]): Defaults to `"card"`.
        text (str): Markdown string to create card title/text that should adhere to the CommonMark Spec.
        href (str): URL (relative or absolute) to navigate to. If not provided the Card serves as a text card
            only. Defaults to `""`.

    """

    type: Literal["card"] = "card"
    text: str = Field(
        ..., description="Markdown string to create card title/text that should adhere to the CommonMark Spec."
    )
    href: str = Field(
        "",
        description="URL (relative or absolute) to navigate to. If not provided the Card serves as a text card only.",
    )

    @validator("href", always=True)
    def set_href(cls, href) -> str:
        if href and _is_relative_url(href):
            return _clean_url(href, "-_/")
        return href

    @_log_call
    def build(self):
        text = dcc.Markdown(self.text, className="card_text", dangerously_allow_html=False, id=self.id)
        card_content = (
            dbc.NavLink(
                text,
                href=get_relative_path(self.href) if _is_relative_url(self.href) else self.href,
                className="card-link",
            )
            if self.href
            else text
        )
        card_container = "nav_card_container" if self.href else "card_container"
        return html.Div(card_content, className=card_container, id=f"{self.id}_outer")
