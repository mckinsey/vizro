from datetime import date
from typing import Annotated, Any, Literal, Optional, Union

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import html
from pydantic import AfterValidator, Field, PrivateAttr
from pydantic.functional_serializers import PlainSerializer
from pydantic.json_schema import SkipJsonSchema

from vizro.models import Action, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._components.form._form_utils import validate_date_picker_range, validate_max, validate_range_value
from vizro.models._models_utils import _log_call


class DatePicker(VizroBaseModel):
    """Temporal single/range option selector `DatePicker`.

    Can be provided to [`Filter`][vizro.models.Filter] or [`Parameter`][vizro.models.Parameter].

    Args:
        type (Literal["date_picker"]): Defaults to `"date_picker"`.
        min (Optional[date]): Start date for date picker. Defaults to `None`.
        max (Optional[date]): End date for date picker. Defaults to `None`.
        value (Optional[Union[list[date], date]]): Default date/dates for date picker. Defaults to `None`.
        title (str): Title to be displayed. Defaults to `""`.
        range (bool): Boolean flag for displaying range picker. Defaults to `True`.
        actions (list[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.
        extra (Optional[dict[str, Any]]): Extra keyword arguments that are passed to `dmc.DatePickerInput` and overwrite
            any defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dmc documentation](https://www.dash-mantine-components.com/components/datepicker)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.

    """

    type: Literal["date_picker"] = "date_picker"
    min: Optional[date] = Field(default=None, description="Start date for date picker.")
    max: Annotated[
        Optional[date], AfterValidator(validate_max), Field(default=None, description="End date for date picker.")
    ]
    value: Annotated[
        Optional[Union[list[date], date]],
        # TODO[MS]: check here and similar if the early exit clause in below validator or similar is
        #  necessary given we don't validate on default
        AfterValidator(validate_range_value),
        Field(default=None, description="Default date/dates for date picker."),
    ]
    title: str = Field(default="", description="Title to be displayed.")
    range: Annotated[
        bool,
        AfterValidator(validate_date_picker_range),
        Field(default=True, description="Boolean flag for displaying range picker.", validate_default=True),
    ]
    actions: Annotated[
        list[Action],
        AfterValidator(_action_validator_factory("value")),
        PlainSerializer(lambda x: x[0].actions),
        Field(default=[]),
    ]
    extra: SkipJsonSchema[
        Annotated[
            dict[str, Any],
            Field(
                default={},
                description="""Extra keyword arguments that are passed to `dmc.DatePickerInput` and overwrite
            any defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dmc documentation](https://www.dash-mantine-components.com/components/datepicker)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.""",
            ),
        ]
    ]

    _dynamic: bool = PrivateAttr(False)

    _input_property: str = PrivateAttr("value")

    def __call__(self, min, max, current_value=None):
        # TODO: Refactor value calculation logic after the Dash persistence bug is fixed and "Select All" PR is merged.
        #  The underlying component's value calculation will need to account for:
        #  - Changes introduced by Pydantic V2.
        #  - The way how the new Vizro solution is built on top of the Dash persistence bugfix.
        #  - Whether the current value is included in the updated options.
        #  - The way how the validate_options_dict validator and tests are improved.
        defaults = {
            "id": self.id,
            "minDate": min,
            "value": self.value or ([min, max] if self.range else min),
            "maxDate": max,
            "persistence": True,
            "persistence_type": "session",
            "type": "range" if self.range else "default",
            "allowSingleDateInRange": True,
            # Required for styling to remove gaps between cells
            "withCellSpacing": False,
        }

        return html.Div(
            children=[
                dbc.Label(children=self.title, html_for=self.id) if self.title else None,
                dmc.DatePickerInput(**(defaults | self.extra)),
            ],
        )

    def _build_dynamic_placeholder(self):
        if not self.value:
            self.value = [self.min, self.max] if self.range else self.min  # type: ignore[list-item]

        return self.__call__(self.min, self.max)

    @_log_call
    def build(self):
        return self._build_dynamic_placeholder() if self._dynamic else self.__call__(self.min, self.max)
