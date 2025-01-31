from datetime import date
from typing import Annotated, Literal, Optional, Union

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import html
from pydantic import AfterValidator, Field, PrivateAttr
from pydantic.functional_serializers import PlainSerializer

from vizro.models import Action, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._components.form._form_utils import validate_date_picker_range, validate_max, validate_range_value


class DatePicker(VizroBaseModel):
    """Temporal single/range option selector `DatePicker`.

    Can be provided to [`Filter`][vizro.models.Filter] or [`Parameter`][vizro.models.Parameter].
    Based on the underlying [`dmc.DatePicker`](https://www.dash-mantine-components.com/components/datepicker) or
    [`dmc.DateRangePicker`](https://www.dash-mantine-components.com/components/datepicker#daterangepicker).

    Args:
        type (Literal["date_picker"]): Defaults to `"date_picker"`.
        min (Optional[date]): Start date for date picker. Defaults to `None`.
        max (Optional[date]): End date for date picker. Defaults to `None`.
        value (Optional[Union[list[date], date]]): Default date/dates for date picker. Defaults to `None`.
        title (str): Title to be displayed. Defaults to `""`.
        range (bool): Boolean flag for displaying range picker. Defaults to `True`.
        actions (list[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.

    """

    type: Literal["date_picker"] = "date_picker"
    min: Optional[date] = Field(default=None, description="Start date for date picker.")
    max: Annotated[
        Optional[date], AfterValidator(validate_max), Field(default=None, description="End date for date picker.")
    ]
    value: Annotated[
        Optional[Union[list[date], date]],
        # TODO[MS]: check here and similar if the early exit clause in below validator or similar is
        # necessary given we don't validate on default
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

    _input_property: str = PrivateAttr("value")

    def build(self):
        init_value = self.value or ([self.min, self.max] if self.range else self.min)  # type: ignore[list-item]

        date_picker = dmc.DatePickerInput(
            id=self.id,
            minDate=self.min,
            value=init_value,
            maxDate=self.max,
            persistence=True,
            persistence_type="session",
            type="range" if self.range else "default",
            allowSingleDateInRange=True,
            # Required for styling to remove gaps between cells
            withCellSpacing=False,
        )

        return html.Div(
            children=[
                dbc.Label(children=self.title, html_for=self.id) if self.title else None,
                date_picker,
            ],
        )
