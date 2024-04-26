from typing import List, Literal, Optional, Union

import dash_mantine_components as dmc
from dash import ClientsideFunction, Input, Output, State, clientside_callback, dcc, html

try:
    from pydantic.v1 import Field, PrivateAttr, validator
except ImportError:  # pragma: no cov
    from pydantic import Field, PrivateAttr, validator


import datetime
from datetime import date

import dash_bootstrap_components as dbc

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
        value (Union[List[date], date]): Default date/dates for date picker. Defaults to `None`.
        title (str): Title to be displayed. Defaults to `""`.
        range (bool): Boolean flag for displaying range picker. Default to `True`.
        actions (List[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.

    """

    type: Literal["date_picker"] = "date_picker"
    min: Optional[date] = Field(None, description="Start date for date picker.")
    max: Optional[date] = Field(None, description="End date for date picker.")
    value: Optional[Union[List[date], date]] = Field(None, description="Default date for date picker")
    title: str = Field("", description="Title to be displayed.")
    range: bool = Field(True, description="Boolean flag for displaying range picker.")
    actions: List[Action] = []

    _input_property: str = PrivateAttr("value")
    _set_actions = _action_validator_factory("value")

    # Re-used validators
    _validate_value = validator("value", allow_reuse=True)(validate_range_value)
    _validate_max = validator("max", allow_reuse=True)(validate_max)
    _validate_range = validator("range", allow_reuse=True, always=True)(validate_date_picker_range)

    def build(self):
        init_value = self.value or ([self.min, self.max] if self.range else self.min)  # type: ignore[list-item]
        date_range_picker_kwargs = {"allowSingleDateInRange": True} if self.range else {}

        output = [
            Output(self.id, "value"),
            Output(f"{self.id}_input_store", "data"),
        ]
        inputs = [
            Input(self.id, "value"),
            State(f"{self.id}_input_store", "data"),
        ]

        clientside_callback(
            ClientsideFunction(namespace="clientside", function_name="update_date_picker_values"),
            output=output,
            inputs=inputs,
        )
        # clientside callback is required as a workaround when the date-picker is overflowing its parent container
        # if there is not enough space. Caused by another workaround for this issue:
        # https://github.com/snehilvj/dash-mantine-components/issues/219
        clientside_callback(
            ClientsideFunction(namespace="clientside", function_name="update_date_picker_position"),
            output=Output(self.id, "dropdownPosition"),
            inputs=Input(self.id, "n_clicks"),
        )

        date_picker_class = dmc.DateRangePicker if self.range else dmc.DatePicker

        # dropdownPosition must be set to bottom-start as a workaround for issue:
        # https://github.com/snehilvj/dash-mantine-components/issues/219
        # clearable must be set to False as a workaround for issue:
        # https://github.com/snehilvj/dash-mantine-components/issues/212
        # maxDate must be increased by one day, and later on disabledDates must be set as maxDate + 1 day
        # as a workaround for issue: https://github.com/snehilvj/dash-mantine-components/issues/230
        date_picker = date_picker_class(
            id=self.id,
            minDate=self.min,
            value=init_value,
            maxDate=self.max + datetime.timedelta(days=1) if self.max else None,
            persistence=True,
            persistence_type="session",
            dropdownPosition="bottom-start",
            clearable=False,
            disabledDates=self.max + datetime.timedelta(days=1) if self.max else None,
            className="datepicker",
            **date_range_picker_kwargs,
        )

        return html.Div(
            [
                dbc.Label(self.title, html_for=self.id) if self.title else None,
                date_picker,
                dcc.Store(id=f"{self.id}_input_store", storage_type="session", data=init_value),
            ],
            className="selector_container",
            id=f"{self.id}_outer",
        )
