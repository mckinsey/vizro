from typing import Literal

import dash_bootstrap_components as dbc
from dash import html
from pydantic import Field, PrivateAttr

from vizro.models import VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._models_utils import _log_call
from vizro.models.types import ActionType


class TextArea(VizroBaseModel):
    """Multi-line text input component `TextArea`.

    Based on the underlying [`dcc.TextArea`](https://dash.plotly.com/dash-core-components/textarea).

    Args:
        type (Literal["text_area"]): Defaults to `"text_area"`.
        title (str): Title to be displayed. Defaults to `""`.
        placeholder (str): Default text to display in input field. Defaults to `""`.
        actions (Optional[list[ActionType]]): Defaults to `[]`.

    """

    type: Literal["text_area"] = "text_area"
    # TODO: before making public consider naming this field (or giving an alias) label instead of title
    title: str = Field(default="", description="Title to be displayed")
    placeholder: str = Field(default="", description="Default text to display in input field")
    actions: list[ActionType] = []

    # Component properties for actions and interactions
    _input_property: str = PrivateAttr("value")

    # Reused validators
    # TODO: Before making public, consider how actions should be triggered and what the default property should be
    # See comment thread: https://github.com/mckinsey/vizro/pull/298#discussion_r1478137654
    _set_actions = _action_validator_factory("value")

    @_log_call
    def build(self):
        return html.Div(
            children=[
                dbc.Label(self.title, html_for=self.id) if self.title else None,
                dbc.Textarea(
                    id=self.id,
                    placeholder=self.placeholder,
                    persistence=True,
                    persistence_type="session",
                    debounce=True,
                ),
            ],
        )
