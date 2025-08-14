from typing import Annotated, Any, Literal, Optional

import dash_bootstrap_components as dbc
from dash import get_relative_path, html
from pydantic import AfterValidator, BeforeValidator, Field, ValidationInfo
from pydantic.functional_serializers import PlainSerializer
from pydantic.json_schema import SkipJsonSchema

from vizro.models import Tooltip, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._models_utils import _log_call, validate_icon
from vizro.models._tooltip import coerce_str_to_tooltip
from vizro.models.types import ActionType, _IdProperty


def validate_text(text, info: ValidationInfo):
    icon = info.data.get("icon")

    if not text and not icon:
        raise ValueError("Please provide either the text or icon argument.")

    return text


class Button(VizroBaseModel):
    """Component provided to `Page` to trigger any defined `action` in `Page`.

    Args:
        type (Literal["button"]): Defaults to `"button"`.
        icon (str): Icon name from [Google Material icons library](https://fonts.google.com/icons). Defaults to `""`.
        text (str): Text to be displayed on button. Defaults to `"Click me!"`.
        href (str): URL (relative or absolute) to navigate to. Defaults to `""`.
        actions (list[ActionType]): See [`ActionType`][vizro.models.types.ActionType]. Defaults to `[]`.
        variant (Literal["plain", "filled", "outlined"]): Predefined styles to choose from. Options are `plain`,
            `filled` or `outlined`. Defaults to `filled`.
        description (Optional[Tooltip]): Optional markdown string that adds an icon next to the button text.
            Hovering over the icon shows a tooltip with the provided description. Defaults to `None`.
        extra (Optional[dict[str, Any]]): Extra keyword arguments that are passed to `dbc.Button` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dbc documentation](https://www.dash-bootstrap-components.com/docs/components/button/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.

    """

    type: Literal["button"] = "button"
    icon: Annotated[
        str,
        AfterValidator(validate_icon),
        Field(description="Icon name from Google Material icons library.", default=""),
    ]
    text: Annotated[
        str, AfterValidator(validate_text), Field(description="Text to be displayed on button.", default="Click me!")
    ]
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
            Visit the [dbc documentation](https://www.dash-bootstrap-components.com/docs/components/button/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.""",
            ),
        ]
    ]

    @property
    def _action_outputs(self) -> dict[str, _IdProperty]:
        return {
            "text": f"{self.id}.children",
            **({"description": f"{self.description.id}-text.children"} if self.description else {}),
        }

    @_log_call
    def build(self):
        variants = {"plain": "link", "filled": "primary", "outlined": "secondary"}
        description = self._build_description()
        icon = (
            html.Span(self.icon, id=f"{self.id}-icon", className="material-symbols-outlined tooltip-icon")
            if self.icon
            else None,
        )

        defaults = {
            "id": self.id,
            "children": html.Span([*icon, self.text, *description], className="btn-text"),
            "href": get_relative_path(self.href) if self.href.startswith("/") else self.href,
            "target": "_top",
            # dbc.Button includes `btn btn-primary` as a class by default and appends any class names provided.
            # To prevent unnecessary class chaining, the button's style variant should be specified using `color`.
            "color": variants[self.variant],
            "class_name": "btn-circular" if self.icon and not self.text else "",
        }

        return dbc.Button(**(defaults | self.extra))

    def _build_description(self):
        """Builds and returns the description elements. If text='' tooltip icon is not rendered and tooltip target
        is reassigned to the button icon.
        """
        if not self.description:
            return [None]

        description = self.description.build().children
        if not self.text:
            description_tooltip = description[1]
            description_tooltip.target = f"{self.id}-icon"
            return [description_tooltip]

        return description
