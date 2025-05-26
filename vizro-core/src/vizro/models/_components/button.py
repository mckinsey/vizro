from typing import Annotated, Any, Literal

import dash_bootstrap_components as dbc
from dash import get_relative_path
from pydantic import AfterValidator, Field
from pydantic.functional_serializers import PlainSerializer
from pydantic.json_schema import SkipJsonSchema

from vizro.models import VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._models_utils import _log_call
from vizro.models.types import ActionType, _IdProperty


class Button(VizroBaseModel):
    """Component provided to `Page` to trigger any defined `action` in `Page`.

    Args:
        type (Literal["button"]): Defaults to `"button"`.
        text (str): Text to be displayed on button. Defaults to `"Click me!"`.
        href (str): URL (relative or absolute) to navigate to. Defaults to `""`.
        actions (list[ActionType]): See [`ActionType`][vizro.models.types.ActionType]. Defaults to `[]`.
        variant (Literal["plain", "filled", "outlined"]): Predefined styles to choose from. Options are `plain`,
            `filled` or `outlined`. Defaults to `filled`.
        extra (Optional[dict[str, Any]]): Extra keyword arguments that are passed to `dbc.Button` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dbc documentation](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/button/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.

    """

    type: Literal["button"] = "button"
    text: str = Field(default="Click me!", description="Text to be displayed on button.")
    href: str = Field(default="", description="URL (relative or absolute) to navigate to.")
    actions: Annotated[
        list[ActionType],
        AfterValidator(_action_validator_factory("n_clicks")),
        PlainSerializer(lambda x: x[0].actions),
        Field(default=[]),
    ]
    variant: Literal["plain", "filled", "outlined"] = Field(
        default="filled",
        description="Predefined styles to choose from. Options are `plain`, `filled` or `outlined`."
        "Defaults to `filled`.",
    )
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

    @property
    def _action_outputs(self) -> dict[str, _IdProperty]:
        return {
            "text": f"{self.id}.children",
        }

    @_log_call
    def build(self):
        variants = {"plain": "link", "filled": "primary", "outlined": "secondary"}

        defaults = {
            "id": self.id,
            "children": self.text,
            "href": get_relative_path(self.href) if self.href.startswith("/") else self.href,
            "target": "_top",
            # dbc.Button includes `btn btn-primary` as a class by default and appends any class names provided.
            # To prevent unnecessary class chaining, the button's style variant should be specified using `color`.
            "color": variants[self.variant],
        }

        return dbc.Button(**(defaults | self.extra))
