"""VizroAI UI dashboard configuration."""

import json

import black
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import vizro.models as vm
import vizro.plotly.express as px
from actions import data_upload_action, display_filename, run_vizro_ai, update_table
from components import (
    CodeClipboard,
    CustomDashboard,
    DropdownMenu,
    HeaderComponent,
    Icon,
    Modal,
    MyDropdown,
    OffCanvas,
    ToggleSwitch,
    UserPromptTextArea,
    UserUpload,
    custom_table,
)
from dash import Input, Output, State, callback, ctx, dcc, get_asset_url, html
from vizro import Vizro

try:
    from langchain_anthropic import ChatAnthropic
except ImportError:
    ChatAnthropic = None

try:
    from langchain_mistralai import ChatMistralAI
except ImportError:
    ChatMistralAI = None

vm.Container.add_type("components", UserUpload)
vm.Container.add_type("components", MyDropdown)
vm.Container.add_type("components", OffCanvas)
vm.Container.add_type("components", CodeClipboard)
vm.Container.add_type("components", Icon)
vm.Container.add_type("components", Modal)
vm.Container.add_type("components", ToggleSwitch)
vm.Container.add_type("components", UserPromptTextArea)
vm.Container.add_type("components", DropdownMenu)
vm.Container.add_type("components", HeaderComponent)

vm.Page.add_type("components", UserUpload)
vm.Page.add_type("components", MyDropdown)
vm.Page.add_type("components", OffCanvas)
vm.Page.add_type("components", CodeClipboard)
vm.Page.add_type("components", Icon)
vm.Page.add_type("components", Modal)


SUPPORTED_MODELS = {
    "OpenAI": [
        "gpt-4o-mini",
        "gpt-4o",
        "gpt-4",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
    ],
    "Anthropic": [
        "claude-3-opus-latest",
        "claude-3-5-sonnet-latest",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ],
    "Mistral": ["mistral-large-latest", "open-mistral-nemo", "codestral-latest"],
}


plot_page = vm.Page(
    id="vizro_ai_plot_page",
    title="Vizro-AI - create interactive charts with Plotly and Vizro",
    layout=vm.Layout(
        grid=[
            [4, 4, 4, 4],
            [2, 2, 1, 1],
            [2, 2, 1, 1],
            [3, 3, 1, 1],
            [3, 3, 1, 1],
            [3, 3, 1, 1],
            *[[0, 0, 1, 1]] * 8,
        ]
    ),
    components=[
        vm.Container(
            title="",
            components=[CodeClipboard(id="plot"), ToggleSwitch(id="toggle-id")],
            layout=vm.Layout(
                grid=[*[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]] * 7, [-1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 1]],
                row_gap="12px",
                col_gap="12px",
            ),
        ),
        vm.Container(
            title="",
            layout=vm.Layout(
                grid=[
                    *[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]] * 10,
                    [-1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 1],
                ]
            ),
            components=[
                vm.Graph(id="graph-id", figure=px.scatter(pd.DataFrame())),
                DropdownMenu(id="dropdown-menu"),
            ],
        ),
        vm.Container(
            id="upload-data-container",
            title="Turn your data into visuals — just upload, describe, and see your chart in action",
            layout=vm.Layout(
                grid=[
                    [1],
                    [0],
                ],
                row_gap="0px",
                # row_min_height="40px",
            ),
            components=[
                UserUpload(
                    id="data-upload-id",
                    actions=[
                        vm.Action(
                            function=data_upload_action(),
                            inputs=["data-upload-id.contents", "data-upload-id.filename"],
                            outputs=["data-store-id.data", "modal-table-icon.style", "modal-table-tooltip.style"],
                        ),
                        vm.Action(
                            function=display_filename(),
                            inputs=["data-store-id.data"],
                            outputs=["upload-message-id.children"],
                        ),
                        vm.Action(
                            function=update_table(),
                            inputs=["data-store-id.data"],
                            outputs=["modal-table.children", "modal-title.children"],
                        ),
                    ],
                ),
                vm.Figure(id="show-data-component", figure=custom_table(data_frame=pd.DataFrame())),
            ],
        ),
        vm.Container(
            title="",
            layout=vm.Layout(
                grid=[
                    [3, 3, 3, 3, 3, 3, 3, 3, 3],
                    [3, 3, 3, 3, 3, 3, 3, 3, 3],
                    [3, 3, 3, 3, 3, 3, 3, 3, 3],
                    [2, -1, -1, -1, -1, 1, 1, 0, 0],
                ],
                row_gap="10px",
                col_gap="4px",
            ),
            components=[
                vm.Button(
                    id="trigger-button-id",
                    text="Run Vizro-AI",
                    actions=[
                        vm.Action(
                            function=run_vizro_ai(),
                            inputs=[
                                "text-area-id.value",
                                "trigger-button-id.n_clicks",
                                "data-store-id.data",
                                "model-dropdown-id.value",
                                "settings-api-key.value",
                                "settings-api-base.value",
                                "settings-dropdown.value",
                            ],
                            outputs=["plot-code-markdown.children", "graph-id.figure", "code-output-store-id.data"],
                        ),
                    ],
                ),
                MyDropdown(
                    options=SUPPORTED_MODELS["OpenAI"], value="gpt-4o-mini", multi=False, id="model-dropdown-id"
                ),
                OffCanvas(id="settings", options=["OpenAI", "Anthropic", "Mistral"], value="OpenAI"),
                UserPromptTextArea(id="text-area-id"),
                # Modal(id="modal"),
            ],
        ),
        vm.Container(
            title="",
            components=[HeaderComponent()],
        ),
    ],
)


dashboard = CustomDashboard(pages=[plot_page])


# pure dash callbacks


@callback(
    Output("settings", "is_open"),
    Input("open-settings-id", "n_clicks"),
    [State("settings", "is_open")],
)
def open_settings(n_clicks, is_open):
    """Callback for opening and closing offcanvas settings component."""
    return not is_open if n_clicks else is_open


@callback(
    Output("settings-api-key", "type"),
    Input("settings-api-key-toggle", "value"),
)
def show_api_key(value):
    """Callback to show api key."""
    return "text" if value else "password"


@callback(
    Output("settings-api-base", "type"),
    Input("settings-api-base-toggle", "value"),
)
def show_api_base(value):
    """Callback to show api base."""
    return "text" if value else "password"


@callback(
    Output("plot-code-markdown", "children"),
    Input("toggle-switch", "value"),
    [State("code-output-store-id", "data")],
)
def toggle_code(value, data):
    """Callback for switching between vizro and plotly code."""
    if not data:
        return dash.no_update

    ai_code = data["ai_outputs"]["vizro"]["code"] if value else data["ai_outputs"]["plotly"]["code"]

    formatted_code = black.format_str(ai_code, mode=black.Mode(line_length=100))
    ai_response = "\n".join(["```python", formatted_code, "```"])
    return ai_response


@callback(
    Output("data-modal", "is_open"),
    Input("modal-table-icon", "n_clicks"),
    State("data-modal", "is_open"),
    State("data-store-id", "data"),
)
def open_modal(n_clicks, is_open, data):
    """Callback for opening modal component."""
    if not data:
        return dash.no_update
    if n_clicks:
        return not is_open
    return is_open


@callback(
    Output("download-file", "data"),
    [Input("dropdown-menu-html", "n_clicks"), Input("dropdown-menu-json", "n_clicks")],
    State("code-output-store-id", "data"),
    prevent_initial_call=True,
)
def download_fig(n_clicks_html, n_clicks_json, data):
    """Callback for downloading vizro fig."""
    if not data:
        return dash.no_update
    if not (n_clicks_html or n_clicks_json):
        return dash.no_update

    button_clicked = ctx.triggered_id

    if button_clicked == "dropdown-menu-html":
        vizro_json = json.loads(data["ai_outputs"]["vizro"]["fig"])
        fig = go.Figure(vizro_json)
        graphs_html = pio.to_html(fig)
        return dcc.send_string(graphs_html, filename="vizro_fig.html")

    if button_clicked == "dropdown-menu-json":
        plotly_json = data["ai_outputs"]["plotly"]["fig"]
        return dcc.send_string(plotly_json, "plotly_fig.json")


@callback(
    [Output("model-dropdown-id", "options"), Output("model-dropdown-id", "value")], Input("settings-dropdown", "value")
)
def update_model_dropdown(value):
    """Callback for updating available models."""
    available_models = SUPPORTED_MODELS[value]
    default_model = available_models[0]
    return available_models, default_model


app = Vizro().build(dashboard)
app.dash.layout.children.append(
    html.Div(
        [
            html.Div(
                [
                    "Made using ",
                    html.Img(src=get_asset_url("logo.svg"), id="banner", alt="Vizro logo"),
                    dbc.NavLink("vizro", href="https://github.com/mckinsey/vizro", target="_blank", external_link=True),
                ],
                style={"display": "flex", "flexDirection": "row"},
            ),
        ],
        className="anchor-container",
    )
)

server = app.dash.server
if __name__ == "__main__":
    app.run()
