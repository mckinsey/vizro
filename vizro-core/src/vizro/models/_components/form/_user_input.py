from typing import List, Literal, Optional

import dash_bootstrap_components as dbc
from dash import html
from pydantic import Field

from vizro.models import Action, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._models_utils import _log_call


class UserInput(VizroBaseModel):
    """Component provided to `Form` to allow user text input.

    Args:
        type (Literal["user_input"]): Defaults to `"user_input"`.
        placeholder (Optional[str]): Default text to display in input field. Defaults to `None`.
        actions (Optional[List[Action]]): Defaults to `[]`.
        title (Optional[str]): Title to be displayed. Defaults to `None`.
        input_type (Literal["text", "number", "password", "email", "search", "tel", "url", "range", "hidden"]):
            Type of value to validate user input against. Defaults to 'text'.
    """

    type: Literal["user_input"] = "user_input"
    title: Optional[str] = Field(None, description="Title to be displayed")
    placeholder: Optional[str] = Field(None, description="Default text to display in input field")
    input_type: Literal["text", "number", "password", "email", "search", "tel", "url", "range", "hidden"] = Field(
        "text", description="Type of value to validate user input against. Defaults to 'text'."
    )
    actions: List[Action] = []

    # Re-used validators
    _set_actions = _action_validator_factory("value")

    @_log_call
    def build(self):
        return html.Div(
            [
                html.P(self.title) if self.title else html.Div(hidden=True),
                dbc.Input(
                    id=self.id,
                    placeholder=self.placeholder,
                    type=self.input_type,
                    persistence=True,
                    debounce=True,
                    className="user_input",
                ),
            ],
            className="selector_container",
            id=f"{self.id}_outer",
        )
