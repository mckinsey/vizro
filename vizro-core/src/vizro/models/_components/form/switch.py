from typing import Annotated, Any, Literal, Optional

import dash_bootstrap_components as dbc
from dash import html
from pydantic import AfterValidator, BeforeValidator, Field, PrivateAttr, model_validator
from pydantic.json_schema import SkipJsonSchema

from vizro.models import Tooltip, VizroBaseModel
from vizro.models._models_utils import make_actions_chain, warn_description_without_title
from vizro.models._tooltip import coerce_str_to_tooltip
from vizro.models.types import ActionsType, _IdProperty


class Switch(VizroBaseModel):
    """Boolean single-option selector `Switch`.

    Can be provided to [`Filter`][vizro.models.Filter] or [`Parameter`][vizro.models.Parameter].

    Abstract: Usage documentation
        [How to use boolean selectors](../user-guides/selectors.md/#boolean-selectors)

    Args:
        type (Literal["switch"]): Defaults to `"switch"`.
        value (bool): Initial state of the switch. When `True`, the switch is "on".
            When `False`, the switch is "off". Defaults to `False`.
        title (str): Title/Label to be displayed to the right of the switch. Defaults to `""`.
        description (Optional[Tooltip]): Optional markdown string that adds an icon next to the title.
            Hovering over the icon shows a tooltip with the provided description. Defaults to `None`.
        actions (ActionsType): See [`ActionsType`][vizro.models.types.ActionsType].
        extra (Optional[dict[str, Any]]): Extra keyword arguments that are passed to `dbc.Switch` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dbc documentation](https://www.dash-bootstrap-components.com/docs/components/input/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.
    """

    type: Literal["switch"] = "switch"
    value: bool = Field(
        default=False,
        description="""Initial state of the switch. When `True`, the switch is enabled/on.
        When `False`, the switch is disabled/off. Defaults to `False`.""",
    )
    title: str = Field(default="", description="Title/Label to be displayed to the right of the switch.")
    # TODO: ideally description would have json_schema_input_type=Union[str, Tooltip] attached to the BeforeValidator,
    #  but this requires pydantic >= 2.9.
    description: Annotated[
        Optional[Tooltip],
        BeforeValidator(coerce_str_to_tooltip),
        AfterValidator(warn_description_without_title),
        Field(
            default=None,
            description="""Optional markdown string that adds an icon next to the title.
            Hovering over the icon shows a tooltip with the provided description. Defaults to `None`.""",
        ),
    ]
    actions: ActionsType = []
    extra: SkipJsonSchema[
        Annotated[
            dict[str, Any],
            Field(
                default={},
                description="""Extra keyword arguments that are passed to `dbc.Switch` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dbc documentation](https://www.dash-bootstrap-components.com/docs/components/input/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.""",
            ),
        ]
    ]

    _dynamic: bool = PrivateAttr(False)
    _inner_component_properties: list[str] = PrivateAttr(dbc.Switch().available_properties)

    @model_validator(mode="after")
    def _make_actions_chain(self):
        return make_actions_chain(self)

    @property
    def _action_triggers(self) -> dict[str, _IdProperty]:
        return {"__default__": f"{self.id}.value"}

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

    def build(self):
        description = self.description.build().children if self.description else [None]

        defaults = {
            "id": self.id,
            "value": self.value,
            "label": [html.Span(id=f"{self.id}_title", children=self.title), *description],
            "persistence": True,
            "persistence_type": "session",
        }

        return dbc.Switch(**(defaults | self.extra))
