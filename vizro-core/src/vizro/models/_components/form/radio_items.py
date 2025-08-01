from typing import Annotated, Any, Literal, Optional

import dash_bootstrap_components as dbc
from dash import html
from pydantic import AfterValidator, BeforeValidator, Field, PrivateAttr, model_validator
from pydantic.functional_serializers import PlainSerializer
from pydantic.json_schema import SkipJsonSchema

from vizro.models import Tooltip, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._components.form._form_utils import (
    get_dict_options_and_default,
    validate_options_dict,
    validate_value,
)
from vizro.models._models_utils import _log_call
from vizro.models._tooltip import coerce_str_to_tooltip
from vizro.models.types import ActionType, OptionsType, SingleValueType, _IdProperty


class RadioItems(VizroBaseModel):
    """Categorical single-option selector `RadioItems`.

    Can be provided to [`Filter`][vizro.models.Filter] or
    [`Parameter`][vizro.models.Parameter].

    Args:
        type (Literal["radio_items"]): Defaults to `"radio_items"`.
        options (OptionsType): See [`OptionsType`][vizro.models.types.OptionsType]. Defaults to `[]`.
        value (Optional[SingleValueType]): See [`SingleValueType`][vizro.models.types.SingleValueType].
            Defaults to `None`.
        title (str): Title to be displayed. Defaults to `""`.
        description (Optional[Tooltip]): Optional markdown string that adds an icon next to the title.
            Hovering over the icon shows a tooltip with the provided description. Defaults to `None`.
        actions (list[ActionType]): See [`ActionType`][vizro.models.types.ActionType]. Defaults to `[]`.
        extra (Optional[dict[str, Any]]): Extra keyword arguments that are passed to `dbc.RadioItems` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dbc documentation](https://www.dash-bootstrap-components.com/docs/components/input/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.
    """

    type: Literal["radio_items"] = "radio_items"
    options: OptionsType = []
    value: Annotated[
        Optional[SingleValueType], AfterValidator(validate_value), Field(default=None, validate_default=True)
    ]
    title: str = Field(default="", description="Title to be displayed")
    # TODO: ideally description would have json_schema_input_type=Union[str, Tooltip] attached to the BeforeValidator,
    #  but this requires pydantic >= 2.9.
    description: Annotated[
        Optional[Tooltip],
        BeforeValidator(coerce_str_to_tooltip),
        Field(
            default=None,
            description="""Optional markdown string that adds an icon next to the title.
            Hovering over the icon shows a tooltip with the provided description. Defaults to `None`.""",
        ),
    ]
    actions: Annotated[
        list[ActionType],
        AfterValidator(_action_validator_factory("value")),
        PlainSerializer(lambda x: x[0].actions),
        Field(default=[]),
    ]
    extra: SkipJsonSchema[
        Annotated[
            dict[str, Any],
            Field(
                default={},
                description="""Extra keyword arguments that are passed to `dbc.RadioItems` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dbc documentation](https://www.dash-bootstrap-components.com/docs/components/input/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.""",
            ),
        ]
    ]

    _dynamic: bool = PrivateAttr(False)
    _in_container: bool = PrivateAttr(False)

    # Reused validators
    _validate_options = model_validator(mode="before")(validate_options_dict)

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

    def __call__(self, options):
        dict_options, default_value = get_dict_options_and_default(options=options, multi=False)
        description = self.description.build().children if self.description else [None]

        defaults = {
            "id": self.id,
            "options": dict_options,
            "value": self.value if self.value is not None else default_value,
            "inline": self._in_container,
            "persistence": True,
            "persistence_type": "session",
        }

        return html.Fieldset(
            children=[
                html.Legend(
                    children=[html.Span(id=f"{self.id}_title", children=self.title), *description],
                    className="form-label",
                )
                if self.title
                else None,
                dbc.RadioItems(**(defaults | self.extra)),
            ]
        )

    def _build_dynamic_placeholder(self):
        if self.value is None:
            _, default_value = get_dict_options_and_default(options=self.options, multi=False)
            self.value = default_value  # type: ignore[assignment]

        return self.__call__(self.options)

    @_log_call
    def build(self):
        return self._build_dynamic_placeholder() if self._dynamic else self.__call__(self.options)
