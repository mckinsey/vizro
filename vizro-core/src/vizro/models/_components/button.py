from typing import Annotated, Any, Literal, Optional, Union

import dash_bootstrap_components as dbc
from dash import get_relative_path, html
from pydantic import AfterValidator, BeforeValidator, Field, JsonValue, model_validator
from pydantic.json_schema import SkipJsonSchema

from vizro.models import Tooltip, VizroBaseModel
from vizro.models._models_utils import _log_call, make_actions_chain, validate_icon
from vizro.models._tooltip import coerce_str_to_tooltip
from vizro.models.types import ActionsType, _IdProperty


class Button(VizroBaseModel):
    """Component provided to `Page` to trigger any defined `action` in `Page`.

    Abstract: Usage documentation
        [How to use buttons](../user-guides/button.md)

    Args:
        type (Literal["button"]): Defaults to `"button"`.
        icon (str): Icon name from [Google Material icons library](https://fonts.google.com/icons). Defaults to `""`.
        text (str): Text to be displayed on button. Defaults to `"Click me!"`.
        href (str): URL (relative or absolute) to navigate to. Defaults to `""`.
        actions (ActionsType): See [`ActionsType`][vizro.models.types.ActionsType].
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
    text: Annotated[str, Field(description="Text to be displayed on button.", default="Click me!")]
    href: str = Field(default="", description="URL (relative or absolute) to navigate to.")
    actions: ActionsType = []
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
        # AfterValidator(warn_description_without_title) is not needed here because either 'text' or 'icon' argument
        # is mandatory.
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

    @model_validator(mode="after")
    def validate_text_and_icon(self):
        if not self.text and not self.icon:
            raise ValueError("You must provide either the `text` or `icon` argument.")

        return self

    @model_validator(mode="after")
    def validate_href_and_actions(self):
        if self.href and self.actions:
            raise ValueError("Button cannot have both `href` and `actions` defined.")

        return self

    @model_validator(mode="after")
    def _make_actions_chain(self):
        return make_actions_chain(self)

    @property
    def _action_triggers(self) -> dict[str, _IdProperty]:
        return {"__default__": f"{self.id}.n_clicks"}

    @property
    def _action_outputs(self) -> dict[str, _IdProperty]:
        return {
            "__default__": f"{self.id}.n_clicks",
            "text": f"{self.id}.children",
            **({"description": f"{self.description.id}-text.children"} if self.description else {}),
        }

    @property
    def _action_inputs(self) -> dict[str, _IdProperty]:
        return {"__default__": f"{self.id}.n_clicks"}

    @staticmethod
    def _get_value_from_trigger(value: JsonValue, trigger: int) -> JsonValue:
        """Return the given `value` without modification."""
        return value

    @_log_call
    def build(self):
        variants = {"plain": "link", "filled": "primary", "outlined": "secondary"}
        description = self._build_description()
        icon = (
            html.Span(self.icon, id=f"{self.id}-icon", className="material-symbols-outlined tooltip-icon")
            if self.icon
            else None,
        )
        text = html.Span(self.text, className="btn-text") if self.text else None

        defaults = {
            "id": self.id,
            "children": [*icon, text, *description],
            "href": get_relative_path(self.href) if self.href.startswith("/") else self.href,
            "target": "_top",
            # dbc.Button includes `btn btn-primary` as a class by default and appends any class names provided.
            # To prevent unnecessary class chaining, the button's style variant should be specified using `color`.
            "color": variants[self.variant],
            "class_name": "btn-circular" if not self.text else "",
        }

        return dbc.Button(**(defaults | self.extra))

    def _build_description(self) -> list[Optional[Union[dbc.Tooltip, html.Span]]]:
        """Conditionally returns the tooltip based on the provided `text` and `icon` arguments.

        If text='', the tooltip icon is omitted, and the tooltip text is shown when hovering over the button icon.
        Otherwise, the tooltip icon is displayed.
        """
        if not self.description:
            return [None]

        description_build_obj = self.description.build()
        if not self.text:
            # When there's no text, we don't display the tooltip icon.
            # Instead we update the tooltip target to the button's icon.
            tooltip_component = description_build_obj[self.description.id]
            tooltip_component.target = f"{self.id}-icon"
            return [tooltip_component]

        return description_build_obj.children
