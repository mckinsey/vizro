from typing import List, Literal, Optional

from dash import dcc, html
from pydantic import Field

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models import Action, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._models_utils import _log_call

stocks = px.data.stocks()


class DatePickerRange(VizroBaseModel):
    """DatePickerRange."""

    type: Literal["date_picker_range"] = "date_picker_range"
    start_date: str
    end_date: str
    min_date_allowed: str
    max_date_allowed: str
    title: Optional[str] = Field(None, description="Title to be displayed")
    actions: List[Action] = []

    # Re-used validators
    _set_actions = _action_validator_factory("end_date")
    # _validate_options = root_validator(allow_reuse=True, pre=True)(validate_options_dict)
    # _validate_value = validator("value", allow_reuse=True, always=True)(validate_value)

    @_log_call
    def build(self):
        # full_options, default_value = get_options_and_default(options=self.options, multi=self.multi)
        return html.Div(
            [
                html.P(self.title) if self.title else None,
                dcc.DatePickerRange(
                    id=self.id,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    min_date_allowed=self.min_date_allowed,
                    max_date_allowed=self.max_date_allowed,
                    className="selector_body_date_picker_range",
                ),
            ],
            className="selector_dropdown_date_picker_range",
            id=f"{self.id}_outer",
        )


vm.Filter.add_type("selector", DatePickerRange)

page = vm.Page(
    title="My first page",
    components=[
        vm.Graph(id="line", figure=px.line(stocks, x="date", y="GOOG")),
    ],
    controls=[
        vm.Filter(
            column="date",
            targets=["line"],
            selector=DatePickerRange(
                id="date_picker_range",
                start_date="2018-01-01",
                end_date="2018-03-31",
                min_date_allowed="2018-01-01",
                max_date_allowed="2019-12-31",
            ),
        ),
        # vm.Filter(column="GOOG", targets=["line"],selector=vm.RangeSlider()),
    ],
)

dashboard = vm.Dashboard(pages=[page])

Vizro().build(dashboard).run()
