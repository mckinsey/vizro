"""Chatbot and custom user input component."""

try:
    from pydantic.v1 import Field, validator
except ImportError:
    from pydantic import Field

from typing import List, Literal

import dash_bootstrap_components as dbc
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
                    id="text_area",
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
                id=self.id, type="password", placeholder=self.placeholder, style={"width": "100%", "height": "34px"}
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
                dcc.Clipboard(target_id="code_markdown", className="code-clipboard"),
                dcc.Markdown(markdown_code, id="code_markdown"),
            ],
            className="code-clipboard-container",
        )


class DropdownSettings(vm.VizroBaseModel):
    """Dropdown settings"""

    type: Literal["dropdown_settings"] = "dropdown_settings"
    input_type: str = "password"

    def build(self):
        dropdown = dbc.DropdownMenu(
            label="Menu",
            addon_type="prepend",
            children=[
                dbc.DropdownMenuItem(
                    children=html.Div(
                        dcc.Input(
                            id="api_key1",
                            type=self.input_type,
                            placeholder="Your API key",
                            style={"width": "100%", "height": "34px"},
                        )
                    )
                ),
                dbc.DropdownMenuItem(
                    children=html.Div(
                        dcc.Input(
                            id="api_base1",
                            type=self.input_type,
                            placeholder="Your API base",
                            style={"width": "100%", "height": "34px"},
                        )
                    )
                ),
            ],
        )
        return dropdown
