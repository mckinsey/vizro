from typing import Literal, Optional, Union

import dash_mantine_components as dmc
from dash import html

try:
    from pydantic.v1 import Field, PrivateAttr, validator
except ImportError:  # pragma: no cov
    from pydantic import Field, PrivateAttr, validator


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
        value (Union[list[date], date]): Default date/dates for date picker. Defaults to `None`.
        title (str): Title to be displayed. Defaults to `""`.
        range (bool): Boolean flag for displaying range picker. Default to `True`.
        actions (list[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.

    """

    type: Literal["date_picker"] = "date_picker"
    min: Optional[date] = Field(None, description="Start date for date picker.")
    max: Optional[date] = Field(None, description="End date for date picker.")
    value: Optional[Union[list[date], date]] = Field(None, description="Default date for date picker")
    title: str = Field("", description="Title to be displayed.")
    range: bool = Field(True, description="Boolean flag for displaying range picker.")
    actions: list[Action] = []

    _input_property: str = PrivateAttr("value")
    _set_actions = _action_validator_factory("value")

    # Re-used validators
    _validate_value = validator("value", allow_reuse=True)(validate_range_value)
    _validate_max = validator("max", allow_reuse=True)(validate_max)
    _validate_range = validator("range", allow_reuse=True, always=True)(validate_date_picker_range)

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
