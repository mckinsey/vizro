from typing import Annotated, Literal

import dash_bootstrap_components as dbc
from dash import html
from pydantic import AfterValidator, Field, PlainSerializer, PrivateAttr

from vizro.models import Action, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._models_utils import _log_call


class UserInput(VizroBaseModel):
    """Single-line text input component `UserInput`.

    Based on the underlying [`dcc.Input`](https://dash.plotly.com/dash-core-components/input).

    Args:
        type (Literal["user_input"]): Defaults to `"user_input"`.
        title (str): Title to be displayed. Defaults to `""`.
        placeholder (str): Default text to display in input field. Defaults to `""`.
        actions (Optional[list[Action]]): Defaults to `[]`.

    """

    type: Literal["user_input"] = "user_input"
    # TODO: before making public consider naming this field (or giving an alias) label instead of title
    title: str = Field(default="", description="Title to be displayed")
    placeholder: str = Field(default="", description="Default text to display in input field")
    # TODO: Before making public, consider how actions should be triggered and what the default property should be
    # See comment thread: https://github.com/mckinsey/vizro/pull/298#discussion_r1478137654
    actions: Annotated[
        list[Action],
        AfterValidator(_action_validator_factory("value")),
        PlainSerializer(lambda x: x[0].actions),
        Field(default=[]),
    ]

    # Component properties for actions and interactions
    _input_property: str = PrivateAttr("value")

    @_log_call
    def build(self):
        return html.Div(
            children=[
                dbc.Label(children=self.title, html_for=self.id) if self.title else None,
                dbc.Input(
                    id=self.id,
                    placeholder=self.placeholder,
                    type="text",
                    persistence=True,
                    persistence_type="session",
                    debounce=True,
                ),
            ],
        )
