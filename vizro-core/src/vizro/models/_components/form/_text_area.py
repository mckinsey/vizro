from typing import Annotated, Literal, Optional

import dash_bootstrap_components as dbc
from dash import html
from pydantic import BeforeValidator, Field

from vizro.models import Tooltip, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._models_utils import _log_call
from vizro.models._tooltip import coerce_str_to_tooltip
from vizro.models.types import ActionType, _IdProperty


class TextArea(VizroBaseModel):
    """Multi-line text input component `TextArea`.

    Based on the underlying [`dcc.TextArea`](https://dash.plotly.com/dash-core-components/textarea).

    Args:
        type (Literal["text_area"]): Defaults to `"text_area"`.
        title (str): Title to be displayed. Defaults to `""`.
        description (Optional[Tooltip]): Optional markdown string that adds an icon next to the title.
            Hovering over the icon shows a tooltip with the provided description. Defaults to `None`.
        placeholder (str): Default text to display in input field. Defaults to `""`.
        actions (Optional[list[ActionType]]): Defaults to `[]`.

    """

    type: Literal["text_area"] = "text_area"
    # TODO: before making public consider naming this field (or giving an alias) label instead of title
    title: str = Field(default="", description="Title to be displayed")
    description: Annotated[
        Optional[Tooltip],
        BeforeValidator(coerce_str_to_tooltip),
        Field(
            default=None,
            description="""Optional markdown string that adds an icon next to the title.
            Hovering over the icon shows a tooltip with the provided description. Defaults to `None`.""",
        ),
    ]
    placeholder: str = Field(default="", description="Default text to display in input field")
    actions: list[ActionType] = []

    # Reused validators
    # TODO: Before making public, consider how actions should be triggered and what the default property should be
    # See comment thread: https://github.com/mckinsey/vizro/pull/298#discussion_r1478137654
    _set_actions = _action_validator_factory("value")

    @property
    def _action_outputs(self) -> dict[str, _IdProperty]:
        return {
            "__default__": f"{self.id}.value",
            **({"title": f"{self.id}_title.children"} if self.title else {}),
            **({"description": f"{self.description.id}-text.children"} if self.description else {}),
        }

    @property
    def _action_inputs(self) -> dict[str, _IdProperty]:
        return {"__default__": f"{self.id}.value"}

    @_log_call
    def build(self):
        description = self.description.build().children if self.description else [None]

        return html.Div(
            children=[
                dbc.Label(children=[html.Span(self.title, id=f"{self.id}_title"), *description], html_for=self.id)
                if self.title
                else None,
                dbc.Textarea(
                    id=self.id,
                    placeholder=self.placeholder,
                    persistence=True,
                    persistence_type="session",
                    debounce=True,
                ),
            ],
        )
