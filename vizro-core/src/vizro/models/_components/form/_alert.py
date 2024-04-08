from typing import List, Literal, Optional

import dash_bootstrap_components as dbc
from dash import html

try:
    from pydantic.v1 import Field
except ImportError:  # pragma: no cov
    from pydantic import Field

from vizro.models import Action, VizroBaseModel
from vizro.models._models_utils import _log_call


class Alert(VizroBaseModel):
    """Component `Alert` to provide user feedback.

    Args:
        type (Literal["alert"]): Defaults to `"alert"`.
        text (str): Text to be displayed in the alert.
        is_open (bool): Flag indicating whether alert should be open by default. Defaults to `True`.
        duration (Optional[int]): Duration in milliseconds for the alert to appear. Defaults to `None`.
        actions (List[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.

    """

    type: Literal["alert"] = "alert"
    text: str = Field(..., description="Text to be displayed in the alert.")
    is_open: bool = Field(True, description="Flag indicating whether alert should be open by default.")
    duration: Optional[int] = Field(None, description="Duration in milliseconds for the alert to appear.", ge=0)
    actions: List[Action] = []

    @_log_call
    def build(self):
        return html.Div(
            [
                dbc.Alert(
                    id=self.id,
                    children=[html.P(self.text)],
                    duration=self.duration,
                    is_open=self.is_open,
                    className="alert",
                )
            ],
            className="alert_container",
        )
