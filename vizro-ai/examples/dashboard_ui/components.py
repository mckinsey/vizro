"""Contains custom components used within a dashboard."""

from typing import Annotated, Literal

import black
import dash_bootstrap_components as dbc
import vizro.models as vm
from dash import dcc, get_asset_url, html
from pydantic import AfterValidator, Field, PlainSerializer
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._models_utils import _log_call
from vizro.models.types import ActionType, capture


class UserPromptTextArea(vm.VizroBaseModel):
    """Input component `UserPromptTextArea`.

    Based on the underlying [`dcc.Input`](https://dash.plotly.com/dash-core-components/input).

    Args:
        type (Literal["user_input"]): Defaults to `"user_text_area"`.
        title (str): Title to be displayed. Defaults to `""`.
        placeholder (str): Default text to display in input field. Defaults to `""`.
        actions (list[ActionType]): See [`ActionType`][vizro.models.types.ActionType]. Defaults to `[]`.
    """

    type: Literal["user_text_area"] = "user_text_area"
    actions: Annotated[
        list[ActionType],
        AfterValidator(_action_validator_factory("value")),
        PlainSerializer(lambda x: x[0].actions),
        Field(default=[]),
    ]

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
    """Component enabling data upload."""

    type: Literal["upload"] = "upload"
    actions: Annotated[
        list[ActionType],
        AfterValidator(_action_validator_factory("contents")),
        PlainSerializer(lambda x: x[0].actions),
        Field(default=[]),
    ]

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

        return dcc.Loading(
            html.Div(
                [
                    dcc.Clipboard(target_id=f"{self.id}-code-markdown", className="code-clipboard"),
                    dcc.Markdown(markdown_code, id=f"{self.id}-code-markdown"),
                ],
                className="code-clipboard-container",
            ),
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
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


def create_provider_item(name, url, note=None):
    """Helper function to create a consistent ListGroupItem for each provider."""
    return dbc.ListGroupItem(
        [
            html.Div(
                [
                    html.Span(name, style={"color": "#ffffff"}),
                    (html.Small(note, style={"color": "rgba(255, 255, 255, 0.5)"}) if note else None),
                    html.Span("→", className="float-end", style={"color": "#ffffff"}),
                ],
                className="d-flex justify-content-between align-items-center",
            )
        ],
        href=url,
        target="_blank",
        action=True,
        style={
            "background-color": "transparent",
            "border": "1px solid rgba(255, 255, 255, 0.1)",
            "margin-bottom": "8px",
            "transition": "all 0.2s ease",
            "cursor": "pointer",
        },
        class_name="list-group-item-action hover-effect",
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

        providers = [
            {"name": "OpenAI", "url": "https://openai.com/index/openai-api/"},
            {"name": "Anthropic", "url": "https://docs.anthropic.com/en/api/getting-started"},
            {"name": "Mistral", "url": "https://docs.mistral.ai/getting-started/quickstart/"},
            {"name": "xAI", "url": "https://x.ai/api", "note": ""},
        ]

        api_instructions = html.Div(
            [
                html.Hr(
                    style={
                        "margin": "2rem 0",
                        "border-color": "rgba(255, 255, 255, 0.1)",
                        "border-style": "solid",
                        "border-width": "0 0 1px 0",
                    }
                ),
                html.Div("Get API Keys", className="mb-3", style={"color": "#ffffff"}),
                dbc.ListGroup(
                    [
                        create_provider_item(name=provider["name"], url=provider["url"], note=provider.get("note"))
                        for provider in providers
                    ],
                    flush=True,
                    className="border-0",
                ),
            ],
        )

        offcanvas = dbc.Offcanvas(
            id=self.id,
            children=[
                html.Div(
                    children=[
                        input_groups,
                        api_instructions,
                    ]
                ),
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
        dashboard_build_obj.children.append(dcc.Store(id="data-store", storage_type="session"))
        dashboard_build_obj.children.append(dcc.Store(id="code-output-store", storage_type="session"))
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
                id="upload-message", children=["Upload your data file (csv or excel)"], style={"paddingTop": "10px"}
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
                className="modal-class",
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
                    target="dropdown-menu-div",
                ),
            ],
            id="dropdown-menu-div",
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
                html.Span("settings", className="material-symbols-outlined", id="open-settings"),
                dbc.Tooltip("Settings", target="open-settings"),
            ],
            className="settings-div",
        )

        return html.Div(children=[header, icon], className="custom_header")


class FlexContainer(vm.Container):
    """Custom flex `Container`."""

    type: Literal["flex_container"] = "flex_container"
    title: str = None  # Title exists in vm.Container but we don't want to use it here.

    def build(self):
        """Returns a flex container."""
        return html.Div(
            id=self.id, children=[component.build() for component in self.components], className="flex-container"
        )
