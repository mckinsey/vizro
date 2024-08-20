"""Chatbot and custom user input component."""

try:
    from pydantic.v1 import validator
except ImportError:
    pass

from typing import Literal

import vizro.models as vm
from dash import dcc, html


class LoadingSpinner(vm.VizroBaseModel):  # potential usable for loading
    type: Literal["loading_spinner"] = "loading_spinner"

    def build(self):
        # If self.id is output of the
        return dcc.Loading(
            children=[html.Div(id=self.id, children="", style={"height": "50px", "width": "50px"})], type="circle"
        )


class MyButton(vm.Button):
    type: Literal["my_button"] = "my_button"

    def build(self):
        button_build_obj = super().build()
        button_build_obj.disabled = True
        button_build_obj.style = {"minWidth": "140px"}
        return button_build_obj


class MyCard(vm.Card):
    type: Literal["my_card"] = "my_card"

    def build(self):
        card_build_obj = super().build()
        card_build_obj.id = f"{self.id}_outer_div"
        card_build_obj.style = {"display": "none", "cursor": "pointer"}
        return card_build_obj


class LogsInterval(vm.VizroBaseModel):
    type: Literal["my_interval"] = "my_interval"

    interval: int

    def build(self):
        return dcc.Interval(id=self.id, interval=self.interval, n_intervals=0, disabled=True)
