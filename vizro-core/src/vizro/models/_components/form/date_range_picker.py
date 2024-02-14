from typing import List, Literal, Optional

import dash_mantine_components as dmc
from dash import html

try:
    from pydantic.v1 import Field, validator
except ImportError:  # pragma: no cov
    from pydantic import Field, validator


from vizro.models import VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._components.form._form_utils import validate_date_picker_value, validate_max_date


class DateRangePicker(VizroBaseModel):
    """Temporal multi-selector `DateRangePicker`.

    Can be provided to [`Filter`][vizro.models.Filter] or
    [`Parameter`][vizro.models.Parameter]. Based on the underlying
    [`dmc.DateRangePicker`](https://www.dash-mantine-components.com/components/datepicker#daterangepicker).

    Args:
        value (Optional[List[str]]):
            Default start and end date for date picker. Must be 2 items. Defaults to `[min_date, max_date]`.
        type (Literal["date_range_picker"]): Defaults to `"date_range_picker"`.
        min_date (Optional[str]): Minimum possible date. Defaults to `None`.
        max_date (Optional[str]): Maximum possible date. Defaults to `None`.
        title (str): Title to be displayed. Defaults to `""`.
        description (str): Description to be displayed above the component.
        actions (List[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.

    """

    type: Literal["date_range_picker"] = "date_range_picker"

    min_date: Optional[str] = Field(None, description="Start date value for date range picker.")
    max_date: Optional[str] = Field(None, description="End date value for date range picker.")
    title: str = Field("", description="Title to be displayed.")
    description: str = Field("", description="Description to be displayed above the component.")
    value: Optional[List[str]] = Field(
        [], description="Default start and end date for date picker.", min_items=2, max_items=2
    )

    actions = []

    _input_property: str = "value"
    _set_actions = _action_validator_factory("value")

    # Re-used validators
    _validate_value = validator("value", allow_reuse=True)(validate_date_picker_value)
    _validate_max_date = validator("max_date", allow_reuse=True)(validate_max_date)

    def build(self):
        init_value = self.value or [self.min_date, self.max_date]  # type: ignore[list-item]
        return html.Div(
            [
                html.P(self.title) if self.title else None,
                dmc.DateRangePicker(
                    id=self.id,
                    description=self.description,
                    minDate=self.min_date,
                    value=init_value,
                    allowSingleDateInRange=False,
                    maxDate=self.max_date,
                ),
            ],
            className="selector_container",
            id=f"{self.id}_outer",
        )
