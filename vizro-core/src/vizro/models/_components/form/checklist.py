from typing import Annotated, Any, Literal, Optional

import dash_bootstrap_components as dbc
from dash import ClientsideFunction, Input, Output, State, clientside_callback, html
from pydantic import AfterValidator, BeforeValidator, Field, PrivateAttr, model_validator
from pydantic.json_schema import SkipJsonSchema

from vizro.models import Tooltip, VizroBaseModel
from vizro.models._components.form._form_utils import (
    get_dict_options_and_default,
    validate_options_dict,
    validate_value,
)
from vizro.models._models_utils import (
    _log_call,
    make_actions_chain,
    warn_description_without_title,
)
from vizro.models._tooltip import coerce_str_to_tooltip
from vizro.models.types import ActionsType, MultiValueType, OptionsType, _IdProperty


class Checklist(VizroBaseModel):
    """Categorical multi-option selector `Checklist`.

    Can be provided to [`Filter`][vizro.models.Filter] or
    [`Parameter`][vizro.models.Parameter].

    Abstract: Usage documentation
        [How to use categorical selectors](../user-guides/selectors.md#categorical-selectors)

    Args:
        type (Literal["checklist"]): Defaults to `"checklist"`.
        options (OptionsType): See [`OptionsType`][vizro.models.types.OptionsType]. Defaults to `[]`.
        value (Optional[MultiValueType]): See [`MultiValueType`][vizro.models.types.MultiValueType]. Defaults to `None`.
        title (str): Title to be displayed. Defaults to `""`.
        show_select_all (Optional[bool]): Whether to display the 'Select All' option that allows users to select or
            deselect all available options with a single click. Defaults to `True`.
        description (Optional[Tooltip]): Optional markdown string that adds an icon next to the title.
            Hovering over the icon shows a tooltip with the provided description. Defaults to `None`.
        actions (ActionsType): See [`ActionsType`][vizro.models.types.ActionsType].
        extra (Optional[dict[str, Any]]): Extra keyword arguments that are passed to `dbc.Checklist` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dbc documentation](https://www.dash-bootstrap-components.com/docs/components/input/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.
    """

    type: Literal["checklist"] = "checklist"
    options: OptionsType = []
    value: Annotated[
        Optional[MultiValueType], AfterValidator(validate_value), Field(default=None, validate_default=True)
    ]
    title: str = Field(default="", description="Title to be displayed")
    # TODO: ideally description would have json_schema_input_type=Union[str, Tooltip] attached to the BeforeValidator,
    #  but this requires pydantic >= 2.9.
    show_select_all: bool = Field(
        default=True,
        description="Whether to display the 'Select All' option that allows users to select or deselect all available "
        "options with a single click.",
    )
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
                description="""Extra keyword arguments that are passed to `dbc.Checklist` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dbc documentation](https://www.dash-bootstrap-components.com/docs/components/input/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.""",
            ),
        ]
    ]

    _dynamic: bool = PrivateAttr(False)
    _in_container: bool = PrivateAttr(False)
    _inner_component_properties: list[str] = PrivateAttr(dbc.Checklist().available_properties)

    # Reused validators
    _validate_options = model_validator(mode="before")(validate_options_dict)

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

    def __call__(self, options):
        dict_options, default_value = get_dict_options_and_default(options=options, multi=True)
        value = self.value if self.value is not None else default_value
        description = self.description.build().children if self.description else [None]

        if self.show_select_all:
            # Add the clientside callback only if show_select_all is True
            self._update_checklist_select_all()
            select_all_checkbox = dbc.Checkbox(
                id=f"{self.id}_select_all",
                value=len(value) == len(dict_options),  # type: ignore[arg-type]
                label="Select All",
                persistence=True,
                persistence_type="session",
            )
        else:
            select_all_checkbox = None

        defaults = {
            "id": self.id,
            "options": dict_options,
            "value": value,
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
                html.Div(
                    children=[
                        select_all_checkbox,
                        dbc.Checklist(**(defaults | self.extra)),
                    ],
                    className="checklist-inline" if self._in_container else None,
                ),
            ],
        )

    def _build_dynamic_placeholder(self):
        if self.value is None:
            _, default_value = get_dict_options_and_default(options=self.options, multi=True)
            self.value = default_value  # type: ignore[assignment]

        return self.__call__(self.options)

    @_log_call
    def build(self):
        return self._build_dynamic_placeholder() if self._dynamic else self.__call__(self.options)

    def _update_checklist_select_all(self):
        """Define the clientside callbacks in the page build phase responsible for handling the select_all."""
        clientside_callback(
            ClientsideFunction(namespace="checklist", function_name="update_checklist_select_all"),
            output=[
                Output(f"{self.id}_select_all", "value"),
                Output(self.id, "value", allow_duplicate=True),
            ],
            inputs=[
                Input(f"{self.id}_select_all", "value"),
                Input(self.id, "value"),
                State(self.id, "options"),
                State(f"{self.id}_select_all", "id"),
            ],
            prevent_initial_call="initial_duplicate",
        )
