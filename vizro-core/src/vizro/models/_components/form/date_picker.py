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
from vizro.models._components.form._form_utils import validate_max, validate_value


class DatePicker(VizroBaseModel):
    """Temporal single-selector `DatePicker`.

    Can be provided to [`Filter`][vizro.models.Filter] or [`Parameter`][vizro.models.Parameter].
    Based on the underlying [`dmc.DatePicker`](https://www.dash-mantine-components.com/components/datepicker).

    Args:
        type (Literal["date_picker"]): Defaults to `"date_picker"`.
        min (Optional[date]): Start date for date picker. Defaults to `None`.
        max (Optional[date]): End date for date picker. Defaults to `None`.
        value (List[date]): Default date value for date picker. Defaults to `None`.
        title (str): Title to be displayed. Defaults to `""`.
        actions (List[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.

    """

    type: Literal["date_picker"] = "date_picker"
    min: Optional[date] = Field(None, description="Start date value for date picker.")
    max: Optional[date] = Field(None, description="End date value for date picker.")
    value: Optional[date] = Field(None, description="Default date value for date picker")
    title: str = Field("", description="Title to be displayed.")

    actions: List[Action] = []

    _input_property: str = PrivateAttr("value")
    _set_actions = _action_validator_factory("value")

    # Re-used validators
    _validate_value = validator("value", allow_reuse=True)(validate_value)
    _validate_max_date = validator("max", allow_reuse=True)(validate_max)

    def build(self):
        init_value = self.value or self.min_date
        return html.Div(
            [
                html.P(self.title) if self.title else None,
                dmc.DatePicker(
                    id=self.id,
                    minDate=self.min_date,
                    value=init_value,
                    maxDate=self.max_date,
                    persistence=True,
                    persistence_type="session",
                ),
            ],
            className="selector_container",
            id=f"{self.id}_outer",
        )
