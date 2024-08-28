"""Contains custom components used within a dashboard."""

from typing import List, Literal

import black
import dash_bootstrap_components as dbc
import vizro.models as vm
from dash import dcc, html
from pydantic import PrivateAttr
from vizro.models import Action
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._models_utils import _log_call


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
    actions: List[Action] = []  # noqa: RUF012

    _set_actions = _action_validator_factory("value")

    @_log_call
    def build(self):
        """Returns the text area component to display vizro-ai code output."""
        return html.Div(
            children=[
                dcc.Textarea(
                    id=self.id,
                    placeholder="Describe the chart you want to create, e.g. "
                    "'Visualize the life expectancy per continent.'",
                )
            ]
        )


class UserUpload(vm.VizroBaseModel):
    """Component enabling data upload.

    Args:
        type (Literal["upload"]): Defaults to `"upload"`.
        title (str): Title to be displayed.
        actions (List[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.

    """

    type: Literal["upload"] = "upload"
    actions: List[Action] = []  # noqa: RUF012

    # 'contents' property is input to custom action callback
    _input_property: str = PrivateAttr("contents")
    # change in 'contents' property of Upload component triggers the actions
    _set_actions = _action_validator_factory("contents")

    def build(self):
        """Returns the upload component for data upload."""
        return html.Div(
            [
                dcc.Upload(
                    id=self.id,
                    children=html.Div(
                        ["Drag and Drop or ", html.A("Select Files")], style={"fontColor": "rgba(255, 255, 255, 0.6)"}
                    ),
                ),
            ]
        )


class CodeClipboard(vm.VizroBaseModel):
    """Code snippet with a copy to clipboard button."""

    type: Literal["code_clipboard"] = "code_clipboard"
    code: str = ""
    language: str = "python"

    def build(self):
        """Returns the code clipboard component inside a output text area."""
        code = black.format_str(self.code, mode=black.Mode(line_length=120))
        code = code.strip("'\"")

        markdown_code = "\n".join(["```python", code, "```"])

        return html.Div(
            [
                dcc.Clipboard(target_id=f"{self.id}-code-markdown", className="code-clipboard"),
                dcc.Markdown(markdown_code, id=f"{self.id}-code-markdown"),
            ],
            className="code-clipboard-container",
        )


class MyDropdown(vm.Dropdown):
    """Custom dropdown component."""

    type: Literal["my_dropdown"] = "my_dropdown"

    def build(self):
        """Returns custom dropdown component that cannot be cleared."""
        dropdown_build_obj = super().build()
        dropdown_build_obj.id = f"{self.id}_outer_div"
        dropdown_build_obj.children[1].clearable = False

        return dropdown_build_obj


class OffCanvas(vm.VizroBaseModel):
    """OffCanvas component for settings."""

    type: Literal["offcanvas"] = "offcanvas"
    options: List[str]
    value: str

    def build(self):
        """Returns the off canvas component for settings."""
        input_groups = html.Div(
            [
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("API Key"),
                        dbc.Input(placeholder="API key", type="password", id=f"{self.id}-api-key"),
                        html.Div(
                            dbc.Checklist(
                                id=f"{self.id}-api-key-toggle",
                                options=[{"label": "", "value": False}],
                                switch=True,
                                inline=True,
                            ),
                            id="toggle-div-api-key",
                        ),
                    ],
                    className="mb-3",
                ),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("API base"),
                        dbc.Input(placeholder="(optional) API base", type="password", id=f"{self.id}-api-base"),
                        html.Div(
                            dbc.Checklist(
                                id=f"{self.id}-api-base-toggle",
                                options=[{"label": "", "value": False}],
                                switch=True,
                                inline=True,
                            ),
                            id="toggle-div-api-base",
                        ),
                    ],
                    className="mb-3",
                ),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("Choose your vendor"),
                        dbc.Select(options=self.options, value=self.value, id=f"{self.id}-dropdown"),
                    ],
                    className="mb-3",
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
                    ]
                )
            ],
            title="Settings",
            is_open=True,
        )
        return offcanvas


class MyPage(vm.Page):
    """Custom page."""

    type: Literal["my_page"] = "my_page"

    def pre_build(self):
        """Overwriting pre_build."""
        pass


class Icon(vm.VizroBaseModel):
    """Icon component for settings."""

    type: Literal["icon"] = "icon"

    def build(self):
        """Returns the icon for api settings."""
        return html.Div(
            children=[html.Span("settings", className="material-symbols-outlined", id=self.id)],
            className="settings-div",
        )


class CustomDashboard(vm.Dashboard):
    """Custom Dashboard model."""

    def build(self):
        """Returns custom dashboard."""
        dashboard_build_obj = super().build()
        dashboard_build_obj.children.append(dcc.Store(id="data-store-id", storage_type="session"))
        dashboard_build_obj.children.append(dcc.Store(id="outputs-store-id", storage_type="session"))
        return dashboard_build_obj
