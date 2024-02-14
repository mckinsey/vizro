from typing import Any, List, Literal, Optional

import dash_mantine_components as dmc
from dash import html

try:
    from pydantic.v1 import Field, PrivateAttr, validator
except ImportError:  # pragma: no cov
    from pydantic import validator


from vizro.models import VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._components.form._form_utils import validate_date_picker_value, validate_max_date


class DatePicker(VizroBaseModel):
    """Temporal multi-selector `DatePicker`.

    Can be provided to [`Filter`][vizro.models.Filter] or
    [`Parameter`][vizro.models.Parameter]. Based on the underlying
    [`dmc.DatePicker`](https://www.dash-mantine-components.com/components/datepicker).

    Args:
        value (List[str]): Default date value for date picker. Defaults to `None`.
        type (Literal["date_picker"]): Defaults to `"date_picker"`.
        min_date (Optional[str]): Minimum possible date. Defaults to `None`.
        max_date (Optional[str]): Maximum possible date. Defaults to `None`.
        title (str): Title to be displayed. Defaults to `""`.
        label(Optional[str]):
        actions (List[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.

    """

    type: Literal["date_picker"] = "date_picker"
    title: Optional[str]
    min_date: Optional[Any]
    max_date: Optional[Any]
    value: Optional[List[Any]]
    label: Optional[str]
    description: Optional[str]

    actions = []

    _input_property: str = "value"
    _set_actions = _action_validator_factory("value")

    # Re-used validators
    _validate_value = validator("value", allow_reuse=True)(validate_date_picker_value)
    _validate_max_date = validator("max_date", allow_reuse=True)(validate_max_date)

    def build(self):
        return html.Div(
            [
                html.P(self.title) if self.title else None,
                dmc.DatePicker(
                    id=self.id,
                    label=self.label,
                    description=self.description,
                    minDate=self.min_date,
                    value=self.value,
                    maxDate=self.max_date,
                ),
            ],
            className="selector_container",
            id=f"{self.id}_outer",
        )
