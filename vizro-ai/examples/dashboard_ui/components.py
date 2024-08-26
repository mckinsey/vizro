"""Chatbot and custom user input component."""

try:
    from pydantic.v1 import Field, validator
except ImportError:
    from pydantic import Field

from typing import List, Literal

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import vizro.models as vm
from dash import dcc, html
from pydantic import PrivateAttr
from vizro.models import Action
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._models_utils import _log_call

try:
    from pydantic.v1 import Field
except ImportError:  # pragma: no cov
    pass

import black


class UserPromptTextArea(vm.VizroBaseModel):
    """Input component `UserPromptTextArea`.

    Based on the underlying [`dcc.Input`](https://dash.plotly.com/dash-core-components/input).

    Args:
        type (Literal["user_input"]): Defaults to `"user_text_area"`.
        title (str): Title to be displayed. Defaults to `""`.
        placeholder (str): Default text to display in input field. Defaults to `""`.
        actions (Optional[List[Action]]): Defaults to `[]`.

    """

    type: Literal["user_text_area"] = "user_text_area"
    actions: List[Action] = []

    _set_actions = _action_validator_factory("value")

    @_log_call
    def build(self):
        return html.Div(
            children=[
                dcc.Textarea(
                    id=self.id,
                    placeholder="How can Vizro-AI help you today?",
                )
            ]
        )


class InputForm(vm.VizroBaseModel):
    """VizroAI settings input form."""

    type: Literal["input_form"] = "input_form"
    actions: List[Action] = []
    placeholder: str

    _set_actions = _action_validator_factory("value")

    def build(self):
        return html.Div(
            dcc.Input(
                id=self.id,
                type="password",
                placeholder=self.placeholder,
                style={"width": "100%", "height": "34px"},
                persistence="session",
            )
        )


class UserUpload(vm.VizroBaseModel):
    """Component enabling data upload.

    Args:
        type (Literal["upload"]): Defaults to `"upload"`.
        title (str): Title to be displayed.
        actions (List[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.

    """

    type: Literal["upload"] = "upload"
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
                    children=html.Div(
                        ["Drag and Drop or ", html.A("Select Files")], style={"fontColor": "rgba(255, 255, 255, 0.6)"}
                    ),
                    style={
                        "height": "45px",
                        "lineHeight": "45px",
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        "textAlign": "center",
                        "color": "#d1d1d5",
                        "borderColor": "rgba(43, 46, 57, 1)",
                    },
                ),
            ]
        )


class CodeClipboard(vm.VizroBaseModel):
    """Code snippet with a copy to clipboard button."""

    type: Literal["code_clipboard"] = "code_clipboard"
    code: str = ""
    language: str = "python"

    def build(self):
        """Returns the code clipboard component inside an accordion."""
        code = black.format_str(self.code, mode=black.Mode(line_length=120))
        code = code.strip("'\"")

        markdown_code = "\n".join(["```python", code, "```"])

        return html.Div(
            [
                dcc.Clipboard(target_id=f"{self.id}_code-markdown", className="code-clipboard"),
                dcc.Markdown(markdown_code, id=f"{self.id}_code-markdown"),
            ],
            className="code-clipboard-container",
        )


class Switch(vm.VizroBaseModel):
    """Toggle for api key visibility"""

    type: Literal["input_switch"] = "input_switch"
    actions: List[Action] = []

    _set_actions = _action_validator_factory("checked")

    def build(self):
        return html.Div(
            children=dmc.Switch(
                id=self.id,
                checked=False,
                persistence=True,
                persistence_type="session",
                className="toggle-switch",
            ),
            id="settings",
            style={"paddingTop": "8px"},
        )


class MyCard(vm.Card):
    type: Literal["my_card"] = "my_card"

    def build(self):
        card_build_obj = super().build()
        card_build_obj.id = f"{self.id}_outer_div"
        card_build_obj.style = {"display": "none"}

        return card_build_obj


class MyDropdown(vm.Dropdown):
    type: Literal["my_dropdown"] = "my_dropdown"

    def build(self):
        dropdown_build_obj = super().build()
        dropdown_build_obj.id = f"{self.id}_outer_div"
        dropdown_build_obj.children[1].clearable = False

        return dropdown_build_obj


class OffCanvas(vm.VizroBaseModel):
    """OffCanvas component for settings!"""

    type: Literal["offcanvas"] = "offcanvas"
    options: List[str]
    value: str

    def build(self):
        input_groups = html.Div(
            [
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("API Key"),
                        dbc.Input(placeholder="API key", type="password", id=f"{self.id}_api_key"),
                    ],
                    className="mb-3",
                ),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("API base"),
                        dbc.Input(placeholder="API base", type="password", id=f"{self.id}_api_base"),
                    ],
                    className="mb-3",
                ),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("Choose your vendor"),
                        dbc.Select(options=self.options, value=self.value, id=f"{self.id}_dropdown"),
                    ],
                    className="mb-3",
                ),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText(dbc.Checkbox(id=f"{self.id}_toggle-secrets-id")),
                        dbc.Input(value="Show secrets", disabled=True),
                    ]
                ),
            ],
            className="mb-3",
        )

        offcanvas = dbc.Offcanvas(
            id=self.id,
            children=[
                html.Div(
                    children=[
                        input_groups,
                        dbc.Button("Save secrets", id=f"{self.id}_save-secrets-id"),
                        html.P(children="", id=f"{self.id}_notification"),
                    ]
                )
            ],
            title="Settings",
            is_open=False,
        )
        return offcanvas


class MyPage(vm.Page):
    type: Literal["my_page"] = "my_page"

    def pre_build(self):
        pass
