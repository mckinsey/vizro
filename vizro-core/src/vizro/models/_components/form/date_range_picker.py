from typing import List, Literal, Optional

import dash_mantine_components as dmc
from dash import html

try:
    from pydantic.v1 import Field, PrivateAttr, validator
except ImportError:  # pragma: no cov
    from pydantic import Field, PrivateAttr, validator


from datetime import date

from vizro.models import Action, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._components.form._form_utils import validate_max, validate_range_value


class DateRangePicker(VizroBaseModel):
    """Temporal multi-selector `DateRangePicker`.

    Can be provided to [`Filter`][vizro.models.Filter] or
    [`Parameter`][vizro.models.Parameter]. Based on the underlying
    [`dmc.DateRangePicker`](https://www.dash-mantine-components.com/components/datepicker#daterangepicker).

    Args:
        type (Literal["date_range_picker"]): Defaults to `"date_range_picker"`.
        min (Optional[date]): Start date for date picker. Defaults to `None`.
        max (Optional[date]): End date for date picker. Defaults to `None`.
        value (Optional[List[date]]):
            Default start and end date for date picker. Must be 2 items. Defaults to `[min, max]`.
        title (str): Title to be displayed. Defaults to `""`.
        actions (List[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.

    """

    type: Literal["date_range_picker"] = "date_range_picker"
    min: Optional[date] = Field(None, description="Start date value for date range picker.")
    max: Optional[date] = Field(None, description="End date value for date range picker.")
    value: Optional[List[date]] = Field(
        [], description="Default start and end date for date picker.", min_items=2, max_items=2
    )
    title: str = Field("", description="Title to be displayed.")

    actions: List[Action] = []

    _input_property: str = PrivateAttr("value")
    _set_actions = _action_validator_factory("value")

    # Re-used validators
    _validate_value = validator("value", allow_reuse=True)(validate_range_value)
    _validate_max = validator("max", allow_reuse=True)(validate_max)

    def build(self):
        init_value = self.value or [self.min, self.max]  # type: ignore[list-item]
        return html.Div(
            [
                html.P(self.title) if self.title else None,
                dmc.DateRangePicker(
                    id=self.id,
                    minDate=self.min,
                    value=init_value,
                    maxDate=self.max,
                    persistence=True,
                    persistence_type="session",
                    dropdownPosition="bottom-start",
                    clearable=False,
                ),
            ],
            className="selector_container",
            id=f"{self.id}_outer",
        )
