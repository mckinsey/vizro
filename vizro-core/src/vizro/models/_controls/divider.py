from typing import Dict, Literal

from dash import html

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call


class Divider(VizroBaseModel):
    """Creates a divider utilizing dash html component.

    Args:
        type (Literal["divider"]): Defaults to `"divider"`.
        style (Dict[str, str]): Style dictionary to pass to html component. Default to
            a solid gray line with 100% width.
    """

    type: Literal["divider"] = "divider"
    style: Dict[str, str] = {
        "borderWidth": "0.1vh",
        "width": "100%",
        "borderColor": "#33353f",
        "borderStyle": "solid",
    }

    @_log_call
    def build(self):
        return html.Hr(
            style=self.style,
            className="divider_container",
            id=f"{self.id}_outer",
        )
