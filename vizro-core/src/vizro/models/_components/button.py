from typing import Annotated, Literal

import dash_bootstrap_components as dbc
from dash import get_relative_path
from pydantic import AfterValidator, Field
from pydantic.functional_serializers import PlainSerializer

from vizro.models import Action, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._models_utils import _log_call

from vizro.models.types import ActionsType


class Button(VizroBaseModel):
    """Component provided to `Page` to trigger any defined `action` in `Page`.

    Args:
        type (Literal["button"]): Defaults to `"button"`.
        text (str): Text to be displayed on button. Defaults to `"Click me!"`.
        actions (list[ActionsType]): See [`ActionsType`][vizro.models.types.ActionsType]. Defaults to `[]`.

    """

    type: Literal["button"] = "button"
    text: str = Field(default="Click me!", description="Text to be displayed on button.")
    href: str = Field(default="", description="URL (relative or absolute) to navigate to.")
    actions: Annotated[
        list[ActionsType],
        AfterValidator(_action_validator_factory("n_clicks")),
        PlainSerializer(lambda x: x[0].actions),
        Field(default=[]),
    ]

    @_log_call
    def build(self):
        return dbc.Button(
            id=self.id,
            children=self.text,
            href=get_relative_path(self.href) if self.href.startswith("/") else self.href,
            target="_top",
        )
