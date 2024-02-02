from typing import List, Literal

import dash_bootstrap_components as dbc
from dash import html

try:
    from pydantic.v1 import Field
except ImportError:  # pragma: no cov
    from pydantic import Field

from vizro.models import Action, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._models_utils import _log_call


class UserInput(VizroBaseModel):
    """Component provided to `Form` to allow single-line user input.

    Args:
        type (Literal["user_input"]): Defaults to `"user_input"`.
        title (str): Title to be displayed. Defaults to `""`.
        placeholder (str): Default text to display in input field. Defaults to `""`.
        input_type (Literal["text", "number", "password", "email", "search", "tel", "url"]):
            Type of value to validate user input against. Defaults to `"text"`.
        actions (Optional[List[Action]]): Defaults to `[]`.
    """

    type: Literal["user_input"] = "user_input"
    title: str = Field("", description="Title to be displayed")
    placeholder: str = Field("", description="Default text to display in input field")
    input_type: Literal["text", "number", "password", "email", "search", "tel", "url"] = Field(
        "text", description="Type of input control to render and validate against."
    )
    actions: List[Action] = []

    # Re-used validators
    _set_actions = _action_validator_factory("value")

    @_log_call
    def build(self):
        return html.Div(
            [
                html.Label(self.title, htmlFor=self.id) if self.title else None,
                dbc.Input(
                    id=self.id,
                    placeholder=self.placeholder,
                    # Note that "range" and "hidden" are not included as possible `input_type` as our recommended
                    # approach is using the `Slider` components. Hidden can be achieved via a simple TextCard.
                    type=self.input_type,
                    persistence=True,
                    persistence_type="session",
                    debounce=True,
                    className="user_input",
                ),
            ],
            className="input-container",
            id=f"{self.id}_outer",
        )
