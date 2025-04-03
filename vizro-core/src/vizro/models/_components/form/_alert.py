from typing import Literal, Optional

import dash_bootstrap_components as dbc
from dash import html
from pydantic import Field

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models.types import ActionType


class Alert(VizroBaseModel):
    """Component `Alert` to provide user feedback.

    Args:
        type (Literal["alert"]): Defaults to `"alert"`.
        text (str): Text to be displayed in the alert.
        is_open (bool): Flag indicating whether alert should be open by default. Defaults to `True`.
        duration (Optional[int]): Duration in milliseconds for the alert to appear. Defaults to `None`.
        actions (list[ActionType]): See [`ActionType`][vizro.models.types.ActionType]. Defaults to `[]`.

    """

    type: Literal["alert"] = "alert"
    text: str = Field(description="Text to be displayed in the alert.")
    is_open: bool = Field(True, description="Flag indicating whether alert should be open by default.")
    duration: Optional[int] = Field(default=None, description="Duration in milliseconds for the alert to appear.", ge=0)
    actions: list[ActionType] = []

    @_log_call
    def build(self):
        return html.Div(
            children=[
                dbc.Alert(
                    id=self.id,
                    children=[html.P(self.text)],
                    duration=self.duration,
                    is_open=self.is_open,
                    class_name="alert",
                )
            ],
        )
