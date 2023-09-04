from typing import List, Literal

import dash_bootstrap_components as dbc
from dash import html
from pydantic import Field

from vizro.models import Action, VizroBaseModel
from vizro.models._models_utils import _log_call

ICON_MAPPING = {
    "warning": "\u26A0          - ",
    "default": "",
    "information": "\u24D8          - ",
    "success": "\u2713          - ",
}


class Alert(VizroBaseModel):
    """Component provided to `Form` to provide user feedback."""

    type: Literal["alert"] = "alert"
    icon: Literal["warning", "default", "information", "success"] = Field(
        "default", description="Icon to be displayed next to text in the alert"
    )
    text: str = Field(..., description="Text to be displayed in the alert")
    is_open: bool = Field(False, description="Flag indicating whether alert should open on dashboard start")
    duration: int = Field(500, description="Duration in milliseconds for the alert to appear", ge=0)
    actions: List[Action] = []

    @_log_call
    def build(self):
        alert_text_full = ICON_MAPPING[self.icon] + self.text

        return [
            dbc.Alert(
                [html.P(alert_text_full, className="alert_text")],
                id=self.id,
                duration=self.duration,
                is_open=self.is_open,
                className="alert",
            ),
        ]
