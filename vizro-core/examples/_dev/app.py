"""Example to show dashboard configuration."""

import datetime
import random
from typing import List, Literal, Optional, Union

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from dash import dcc, html
from vizro import Vizro
from vizro.models.types import MultiValueType, OptionsType, SingleValueType

try:
    from pydantic.v1 import Field, PrivateAttr
except ImportError:
    from pydantic import Field, PrivateAttr
from vizro.models import Action
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._base import VizroBaseModel, _log_call

vm.Page.add_type("components", vm.DatePicker)

date_data_frame = pd.DataFrame(
    {
        "value": [random.randint(0, 5) for _ in range(31)],
        "time": [datetime.datetime(2024, 1, 1) + datetime.timedelta(days=i) for i in range(31)],
        "type": [random.choice(["A", "B", "C"]) for _ in range(31)],
    }
)

numerical_selectors = [
    vm.RangeSlider(id="numerical_range_slider"),
    vm.Slider(id="numerical_slider"),
    vm.Dropdown(id="numerical_dropdown"),
    vm.RadioItems(id="numerical_radio_items"),
    vm.Checklist(id="numerical_checklist"),
    # vm.DatePicker(id="numerical_date_picker")  # -> doesn't work properly with numerical column_type
    #    because it's impossible to compare "number" with "date"
]

temporal_selectors = [
    # vm.RangeSlider(id="temporal_range_slider"),  # -> dcc.RangeSlider doesn't work with temporal data
    # vm.Slider(id="temporal_slider"),  # -> dcc.Slider doesn't work with temporal data
    vm.Dropdown(id="temporal_dropdown"),
    vm.RadioItems(id="temporal_radio_items"),
    vm.Checklist(id="temporal_checklist"),
    vm.DatePicker(id="temporal_date_picker"),
]

categorical_selectors = [
    # vm.RangeSlider(id="categorical_range_slider"),  # -> dcc.RangeSlider doesn't work with categorical data
    # vm.Slider(id="categorical_slider"),  # -> dcc.Slider doesn't work with categorical data
    vm.Dropdown(id="categorical_dropdown"),
    vm.RadioItems(id="categorical_radio_items"),
    vm.Checklist(id="categorical_checklist"),
    # vm.DatePicker(id="categorical_date_picker")  # -> dmc.DatePicker doesn't work with categorical data
]

page = vm.Page(
    title="My first page",
    components=[
        vm.Graph(figure=px.line(date_data_frame, x="time", y="value")),
        vm.DatePicker(min="2024-01-01", max="2026-01-01", range=False),
    ],
    controls=[
        # *[vm.Filter(column="value", selector=selector) for selector in numerical_selectors],
        # *[vm.Filter(column="time", selector=selector) for selector in temporal_selectors],
        # *[vm.Filter(column="type", selector=selector) for selector in categorical_selectors],
        vm.Filter(column="type"),
        vm.Filter(column="value"),
        vm.Filter(column="time"),
    ],
)

df_stocks_long = pd.melt(
    px.data.stocks(datetimes=True),
    id_vars="date",
    value_vars=["GOOG", "AAPL", "AMZN", "FB", "NFLX", "MSFT"],
    var_name="stocks",
    value_name="value",
)

df_stocks_long["value"] = df_stocks_long["value"].round(3)

page_2 = vm.Page(
    title="My second page",
    components=[
        vm.Graph(figure=px.line(df_stocks_long, x="date", y="value", color="stocks")),
    ],
    controls=[
        vm.Filter(column="stocks"),
        vm.Filter(column="value"),
        vm.Filter(column="date"),
    ],
)


# CUSTOM SELECTORS


class NewDropdown(VizroBaseModel):
    """Categorical single/multi-selector `Dropdown` to be provided to `Filter`."""

    type: Literal["new-dropdown"] = "new-dropdown"
    options: Optional[OptionsType] = Field(None, description="Possible options the user can select from")
    value: Optional[Union[SingleValueType, MultiValueType]] = Field(
        None, description="Options that are selected by default"
    )
    multi: bool = Field(True, description="Whether to allow selection of multiple values")
    actions: List[Action] = []  # noqa: RUF012
    title: Optional[str] = Field(None, description="Title to be displayed")

    # Component properties for actions and interactions
    _input_property: str = PrivateAttr("value")

    set_actions = _action_validator_factory("value")

    @_log_call
    def build(self):
        """Custom build method."""
        return html.Div(
            [
                html.P(self.title) if self.title else None,
                dcc.Dropdown(
                    id=self.id,
                    options=self.options,
                    value=self.value or self.options[0],
                    multi=self.multi,
                    persistence=True,
                    clearable=False,
                ),
            ],
            className="input-container",
        )


class RangeSliderNonCross(vm.RangeSlider):
    """Custom numeric multi-selector `RangeSliderNonCross` to be provided to `Filter`."""

    type: Literal["range_slider_non_cross"] = "range_slider_non_cross"

    def build(self):
        """Custom build method."""
        range_slider_build_obj = super().build()
        range_slider_build_obj[self.id].allowCross = False
        return range_slider_build_obj


# Important: Add new components to expected type - here the selector of the parent components
vm.Filter.add_type("selector", NewDropdown)
vm.Parameter.add_type("selector", NewDropdown)


# Important: Add new components to expected type - here the selector of the parent components
vm.Filter.add_type("selector", RangeSliderNonCross)
vm.Parameter.add_type("selector", RangeSliderNonCross)


page_3 = vm.Page(
    title="Custom filer selectors",
    components=[
        vm.Graph(figure=px.line(date_data_frame, x="time", y="value")),
    ],
    controls=[
        vm.Filter(column="type", selector=NewDropdown(options=["A", "B", "C"])),
        vm.Filter(column="value", selector=NewDropdown(options=[1, 2, 3, 4, 5])),
        vm.Filter(
            column="time",
            selector=NewDropdown(
                options=[datetime.datetime(2024, 1, 1) + datetime.timedelta(days=i) for i in range(31)]
            ),
        ),
        vm.Filter(column="value", selector=RangeSliderNonCross(id="new_range_slider")),
    ],
)

dashboard = vm.Dashboard(pages=[page, page_2, page_3])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
