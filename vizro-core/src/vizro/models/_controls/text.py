from typing import Literal

from dash import dcc, html

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call


class Text(VizroBaseModel):
    """Creates a text utilizing `dcc.Markdown` as text component.

    Args:
        type (Literal["text"]): Defaults to `"text"`.
        text (str): Markdown string to create text that should adhere to the CommonMark Spec.
    """

    type: Literal["text"] = "text"
    text: str

    @_log_call
    def build(self):
        text = dcc.Markdown(
            self.text,
            className="text",
            dangerously_allow_html=False,
            id=self.id,
        )
        return html.Div(
            text,
            className="text_container",
            id=f"{self.id}_outer",
        )
