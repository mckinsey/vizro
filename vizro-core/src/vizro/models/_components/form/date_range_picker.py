from typing import Any, List, Literal, Optional

import dash_mantine_components as dmc
from dash import html

try:
    from pydantic.v1 import Field, PrivateAttr, validator
except ImportError:  # pragma: no cov
    pass


from vizro.models import VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory


class DateRangePicker(VizroBaseModel):
    type: Literal["date_picker"] = "date_picker"
    title: Optional[str]
    min_date: Optional[Any]
    value: Optional[List[Any]]
    label: Optional[str]
    description: Optional[str]

    actions = []

    _input_property: str = "value"
    _set_actions = _action_validator_factory("value")

    def build(self):
        return html.Div(
            [
                html.P(self.title) if self.title else None,
                dmc.DateRangePicker(
                    id=self.id,
                    label=self.label,
                    description=self.description,
                    minDate=self.min_date,
                    value=self.value,
                ),
            ]
        )
