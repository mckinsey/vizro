"""Contains custom components used within a dashboard."""

from typing import Literal

import black
import dash_bootstrap_components as dbc
import vizro.models as vm
from dash import dcc, get_asset_url, html
from pydantic import PrivateAttr
from vizro.models import Action
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._models_utils import _log_call
from vizro.models.types import capture


class UserPromptTextArea(vm.VizroBaseModel):
    """Input component `UserPromptTextArea`.

    Based on the underlying [`dcc.Input`](https://dash.plotly.com/dash-core-components/input).

    Args:
        type (Literal["user_input"]): Defaults to `"user_text_area"`.
        title (str): Title to be displayed. Defaults to `""`.
        placeholder (str): Default text to display in input field. Defaults to `""`.
        actions (Optional[list[Action]]): Defaults to `[]`.

    """

    type: Literal["user_text_area"] = "user_text_area"
    actions: list[Action] = []  # noqa: RUF012

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
        actions (list[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.

    """

    type: Literal["upload"] = "upload"
    actions: list[Action] = []  # noqa: RUF012

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
                    children=html.Div(["Drag and Drop or ", html.A("Select Files")], id="data-upload"),
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


class Modal(vm.VizroBaseModel):
    """Modal to convey warning message."""

    type: Literal["modal"] = "modal"

    def build(self):
        """Returns the modal component."""
        return dbc.Modal(
            # id=self.id,
            children=[
                dbc.ModalHeader(children=dcc.Markdown("""# Warning""")),
                dbc.ModalBody(
                    children=dcc.Markdown(
                        """### Do NOT upload any sensitive or personally identifying data.

#### Reasoning:
This space is hosted publicly running one server in a single container. Further this UI executes dynamically created
code on the server. It thus cannot guarantee the security of your data. In addition it sends the user query and the
data to the chosen LLM vendor API. This is not an exhaustive list.

#### Alternatives:
If sending your query and data to a LLM is acceptable, you can pull and run this image locally. This will avoid sharing
an instance with others. You can do so by clicking the three dots in the top right of the HuggingFace banner
and click `Run with Docker`.

Always exercise caution when sharing data online and understand your responsibilities regarding data privacy
and security.
"""
                    )
                ),
            ],
            size="l",
            is_open=True,
        )


class OffCanvas(vm.VizroBaseModel):
    """OffCanvas component for settings."""

    type: Literal["offcanvas"] = "offcanvas"
    options: list[str]
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
        dashboard_build_obj.children.append(dcc.Store(id="code-output-store-id", storage_type="session"))
        return dashboard_build_obj


class ToggleSwitch(vm.VizroBaseModel):
    """Custom toggle switch model."""

    type: Literal["toggle_switch"] = "toggle_switch"

    def build(self):
        """Returns custom toggle switch component."""
        toggle_component = html.Div(
            children=[
                html.P("Plotly"),
                html.Div(
                    dbc.Switch(id="toggle-switch", value=True, style={"borderRadius": "8px"}),
                    style={"paddingRight": "4px"},
                ),
                html.P("Vizro"),
            ],
            className="toggle-div",
        )
        return toggle_component


@capture("figure")
def custom_table(data_frame):
    """Custom table figure."""
    table = dbc.Table.from_dataframe(data_frame, striped=False, bordered=True, hover=True)

    table_modal = html.Div(
        [
            html.Span(
                "table_view",
                className="material-symbols-outlined",
                id="modal-table-icon",
                style={"color": "gray", "cursor": "default"},
            ),
            dbc.Tooltip(
                "Click to view data!",
                placement="top",
                target="modal-table-icon",
                style={"display": "none"},
                id="modal-table-tooltip",
            ),
            html.P(
                id="upload-message-id", children=["Upload your data file (csv or excel)"], style={"paddingTop": "10px"}
            ),
            dbc.Modal(
                id="data-modal",
                children=[
                    dbc.ModalHeader(dbc.ModalTitle(id="modal-title", children="No data uploaded!")),
                    dbc.ModalBody(
                        id="modal-table",
                        children=table,
                    ),
                ],
                size="xl",
                modal_class_name="modal-class",
            ),
        ],
        id="table-modal-div",
    )
    return table_modal


class DropdownMenu(vm.VizroBaseModel):
    """Custom dropdown menu component."""

    type: Literal["dropdown_menu"] = "dropdown_menu"

    def build(self):
        """Returns custom dropdown menu."""
        dropdown_menu = dbc.DropdownMenu(
            id="dropdown-menu-button",
            label="Download ",
            children=[
                dbc.DropdownMenuItem(
                    children=[
                        dbc.Button(children="JSON", id=f"{self.id}-json", className="download-button"),
                    ]
                ),
                dbc.DropdownMenuItem(
                    children=[
                        dbc.Button(children="HTML", id=f"{self.id}-html", className="download-button"),
                    ]
                ),
                dcc.Download(id="download-file"),
            ],
            toggleClassName="dropdown-menu-toggle-class",
        )
        download_div = html.Div(
            children=[
                html.Span("download", className="material-symbols-outlined", id=f"{self.id}-icon"),
                dropdown_menu,
                dbc.Tooltip(
                    "Download this plot to your device as a plotly JSON or interactive HTML file "
                    "for easy sharing or future use.",
                    target="dropdown-menu-icon",
                ),
            ],
            id="dropdown-menu-id",
        )

        return download_div


class HeaderComponent(vm.VizroBaseModel):
    """Custom header component."""

    type: Literal["header"] = "header"

    def build(self):
        """Returns custom header component."""
        title = html.Header("Vizro", id="custom-header-title")
        header = html.Div(
            children=[html.Img(src=get_asset_url("logo.svg"), alt="Vizro logo", className="header-logo"), title],
            id="custom-header-div",
        )
        icon = html.Div(
            children=[
                html.Span("settings", className="material-symbols-outlined", id="open-settings-id"),
                dbc.Tooltip("Settings", target="open-settings-id"),
            ],
            className="settings-div",
        )

        return html.Div(children=[header, icon], className="custom_header")
