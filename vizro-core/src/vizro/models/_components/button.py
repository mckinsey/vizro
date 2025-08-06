from typing import Annotated, Any, Literal, Optional

import dash_bootstrap_components as dbc
from dash import get_relative_path, html
from pydantic import BeforeValidator, Field, model_validator
from pydantic.json_schema import SkipJsonSchema

from vizro.models import Tooltip, VizroBaseModel
from vizro.models._models_utils import _log_call, make_actions_chain
from vizro.models._tooltip import coerce_str_to_tooltip
from vizro.models.types import ActionType, _IdProperty


def coerce_actions_type(actions: Any) -> list[Any]:
    """Converts a single action into a list of actions for user convenience."""
    if isinstance(actions, list):
        return actions
    return [actions]


class Button(VizroBaseModel):
    """Component provided to `Page` to trigger any defined `action` in `Page`.

    Args:
        type (Literal["button"]): Defaults to `"button"`.
        text (str): Text to be displayed on button. Needs to have at least 1 character. Defaults to `"Click me!"`.
        href (str): URL (relative or absolute) to navigate to. Defaults to `""`.
        actions (list[ActionType]): See [`ActionType`][vizro.models.types.ActionType].
            Accepts either a single action or a list of actions. Defaults to `[]`.
        variant (Literal["plain", "filled", "outlined"]): Predefined styles to choose from. Options are `plain`,
            `filled` or `outlined`. Defaults to `filled`.
        description (Optional[Tooltip]): Optional markdown string that adds an icon next to the button text.
            Hovering over the icon shows a tooltip with the provided description. Defaults to `None`.
        extra (Optional[dict[str, Any]]): Extra keyword arguments that are passed to `dbc.Button` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dbc documentation](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/button/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.

    """

    type: Literal["button"] = "button"
    text: Annotated[str, Field(default="Click me!", description="Text to be displayed on button.", min_length=1)]
    href: str = Field(default="", description="URL (relative or absolute) to navigate to.")
    actions: Annotated[list["ActionType"], BeforeValidator(coerce_actions_type)] = []
    variant: Literal["plain", "filled", "outlined"] = Field(
        default="filled",
        description="Predefined styles to choose from. Options are `plain`, `filled` or `outlined`."
        "Defaults to `filled`.",
    )
    # TODO: ideally description would have json_schema_input_type=Union[str, Tooltip] attached to the BeforeValidator,
    #  but this requires pydantic >= 2.9.
    description: Annotated[
        Optional[Tooltip],
        BeforeValidator(coerce_str_to_tooltip),
        # AfterValidator(warn_description_without_title) is not needed here because 'text' is mandatory and
        # must have at least one character.
        Field(
            default=None,
            description="""Optional markdown string that adds an icon next to the button text.
            Hovering over the icon shows a tooltip with the provided description. Defaults to `None`.""",
        ),
    ]
    extra: SkipJsonSchema[
        Annotated[
            dict[str, Any],
            Field(
                default={},
                description="""Extra keyword arguments that are passed to `dbc.Button` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dbc documentation](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/button/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.""",
            ),
        ]
    ]

    _make_actions_chain = model_validator(mode="after")(make_actions_chain)

    @property
    def _action_triggers(self) -> dict[str, _IdProperty]:
        return {"__default__": f"{self.id}.n_clicks"}

    @property
    def _action_outputs(self) -> dict[str, _IdProperty]:
        return {
            "text": f"{self.id}.children",
            **({"description": f"{self.description.id}-text.children"} if self.description else {}),
        }

    @_log_call
    def build(self):
        variants = {"plain": "link", "filled": "primary", "outlined": "secondary"}
        description = self.description.build().children if self.description else [None]

        defaults = {
            "id": self.id,
            "children": html.Span([self.text, *description], className="button-text"),
            "href": get_relative_path(self.href) if self.href.startswith("/") else self.href,
            "target": "_top",
            # dbc.Button includes `btn btn-primary` as a class by default and appends any class names provided.
            # To prevent unnecessary class chaining, the button's style variant should be specified using `color`.
            "color": variants[self.variant],
        }

        return dbc.Button(**(defaults | self.extra))
