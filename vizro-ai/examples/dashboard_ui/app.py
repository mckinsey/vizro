"""VizroAI UI dashboard configuration."""

import json

import dash_bootstrap_components as dbc
import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from actions import data_upload_action, display_filename, run_vizro_ai
from components import (
    CodeClipboard,
    CustomDashboard,
    Icon,
    MyDropdown,
    MyPage,
    OffCanvas,
    UserPromptTextArea,
    UserUpload,
)
from dash import Input, Output, State, callback, get_asset_url, html
from dash.exceptions import PreventUpdate
from vizro import Vizro

vm.Container.add_type("components", UserUpload)
vm.Container.add_type("components", MyDropdown)
vm.Container.add_type("components", OffCanvas)
vm.Container.add_type("components", CodeClipboard)
vm.Container.add_type("components", Icon)

MyPage.add_type("components", UserPromptTextArea)
MyPage.add_type("components", UserUpload)
MyPage.add_type("components", MyDropdown)
MyPage.add_type("components", OffCanvas)
MyPage.add_type("components", CodeClipboard)
MyPage.add_type("components", Icon)


SUPPORTED_MODELS = [
    "gpt-4o-mini",
    "gpt-4",
    "gpt-4-turbo",
    "gpt-3.5-turbo",
    "gpt-4o",
]


plot_page = MyPage(
    id="vizro_ai_plot_page",
    title="Vizro-AI - effortlessly create interactive charts with Plotly",
    layout=vm.Layout(
        grid=[
            [3, 3, -1, 5],
            [1, 1, 2, 2],
            [4, 4, 2, 2],
            *[[0, 0, 2, 2]] * 6,
        ]
    ),
    components=[
        vm.Container(title="", components=[CodeClipboard(id="plot")]),
        UserPromptTextArea(
            id="text-area-id",
        ),
        vm.Graph(id="graph-id", figure=px.scatter(pd.DataFrame())),
        vm.Container(
            title="",
            layout=vm.Layout(grid=[[1], [0]], row_gap="0px"),
            components=[
                UserUpload(
                    id="data-upload-id",
                    actions=[
                        vm.Action(
                            function=data_upload_action(),
                            inputs=["data-upload-id.contents", "data-upload-id.filename"],
                            outputs=["data-store-id.data"],
                        ),
                        vm.Action(
                            function=display_filename(),
                            inputs=["data-store-id.data"],
                            outputs=["upload-message-id.children"],
                        ),
                    ],
                ),
                vm.Card(id="upload-message-id", text="Upload your data file (csv or excel)"),
            ],
        ),
        vm.Container(
            title="",
            layout=vm.Layout(grid=[[2, -1, -1, -1, -1, 1, 1, 0, 0]], row_gap="0px", col_gap="4px"),
            components=[
                vm.Button(
                    id="trigger-button-id",
                    text="Run VizroAI",
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
                            outputs=["plot-code-markdown.children", "graph-id.figure", "outputs-store-id.data"],
                        ),
                    ],
                ),
                MyDropdown(options=SUPPORTED_MODELS, value="gpt-4o-mini", multi=False, id="model-dropdown-id"),
                OffCanvas(id="settings", options=["OpenAI"], value="OpenAI"),
            ],
        ),
        Icon(id="open-settings-id"),
    ],
)


dashboard = CustomDashboard(pages=[plot_page])


# pure dash callbacks
@callback(
    [
        Output("plot-code-markdown", "children", allow_duplicate=True),
        Output("graph-id", "figure", allow_duplicate=True),
        Output("text-area-id", "value"),
        Output("upload-message-id", "children"),
    ],
    [Input("on_page_load_action_trigger_vizro_ai_plot_page", "data")],
    [State("outputs-store-id", "data")],
    prevent_initial_call="initial_duplicate",
)
def update_data(page_data, outputs_data):
    """Callback for retrieving latest vizro-ai output from dcc store."""
    if not outputs_data:
        raise PreventUpdate

    ai_response = outputs_data["ai_response"]
    fig = json.loads(outputs_data["figure"])
    filename = f"File uploaded: '{outputs_data['filename']}'"
    prompt = outputs_data["prompt"]

    return ai_response, fig, prompt, filename


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


app = Vizro().build(dashboard)
app.dash.layout.children.append(
    html.Div(
        [
            dbc.NavLink("Contact us", href="https://github.com/mckinsey/vizro/issues"),
            dbc.NavLink("GitHub", href="https://github.com/mckinsey/vizro"),
            dbc.NavLink("Docs", href="https://vizro.readthedocs.io/projects/vizro-ai/"),
            html.Div(
                [
                    "Made using ",
                    html.Img(src=get_asset_url("logo.svg"), id="banner", alt="Vizro logo"),
                    "vizro",
                ],
            ),
        ],
        className="anchor-container",
    )
)


if __name__ == "__main__":
    app.run()
