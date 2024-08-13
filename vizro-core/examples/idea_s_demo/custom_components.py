"""Components"""

from typing import List, Literal

import vizro.models as vm
from dash import dcc, html
from pydantic import PrivateAttr
from vizro.models import Action
from vizro.models._action._actions_chain import _action_validator_factory


class Upload(vm.VizroBaseModel):
    """Component enabling data upload.

    Args:
        type (Literal["upload"]): Defaults to `"upload"`.
        title (str): Title to be displayed.
        actions (List[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.

    """

    type: Literal["upload"] = "upload"
    title: str
    actions: List[Action] = []

    # 'contents' property is input to custom action callback
    _input_property: str = PrivateAttr("contents")
    # change in 'contents' property of Upload component triggers the actions
    _set_actions = _action_validator_factory("contents")

    def build(self):
        return html.Div(
            [
                dcc.Upload(
                    id=self.id,
                    children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
                    style={
                        "height": "45px",
                        "lineHeight": "45px",
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        "textAlign": "center",
                        "color": "#d1d1d5",
                        "borderColor": "#d1d1d5",
                    },
                ),
            ]
        )


class LoadingSpinner(vm.VizroBaseModel):
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
