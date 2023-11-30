from typing import List, Literal

import dash_bootstrap_components as dbc
from dash import html
from pydantic import Field

from vizro.models import Action, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._models_utils import _log_call


class Button(VizroBaseModel):
    """Component provided to `Page` to trigger any defined `action` in `Page`.

    Args:
        type (Literal["button"]): Defaults to `"button"`.
        text (str): Text to be displayed on button. Defaults to `"Click me!"`.
        actions (List[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.
    """

    type: Literal["button"] = "button"
    text: str = Field("Click me!", description="Text to be displayed on button.")
    actions: List[Action] = []

    # Re-used validators
    _set_actions = _action_validator_factory("n_clicks")

    @_log_call
    def build(self):
        return html.Div(
            [
                dbc.Button(
                    id=self.id,
                    children=self.text,
                    className="button_primary",
                ),
            ],
            className="button_container",
            id=f"{self.id}_outer",
        )


class LinkButton(Button):
    href: str

    @_log_call
    def build(self):
        button = super().build()
        button[self.id].href = get_relative_path(self.href)
        return button

        # return html.Div(
        #     [
        #         dbc.Button(
        #             id=self.id,
        #             children=self.text,
        #             className="button_primary",
        #             href=get_relative_path(self.href)
        #         ),
        #     ],
        #     className="button_container",
        #     id=f"{self.id}_outer",
        # )
