"""VizroAI UI dashboard configuration."""

import json

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from components import (
    CodeClipboard,
    MyDropdown,
    MyPage,
    OffCanvas,
    UserPromptTextArea,
    UserUpload,
)
from custom_actions import data_upload_action, display_filename, run_vizro_ai
from dash import Input, Output, State, callback, dcc
from dash.exceptions import PreventUpdate
from vizro import Vizro

vm.Container.add_type("components", UserUpload)
vm.Container.add_type("components", MyDropdown)
vm.Container.add_type("components", OffCanvas)
vm.Container.add_type("components", CodeClipboard)

MyPage.add_type("components", UserPromptTextArea)
MyPage.add_type("components", UserUpload)
MyPage.add_type("components", MyDropdown)
MyPage.add_type("components", OffCanvas)
MyPage.add_type("components", CodeClipboard)


class CustomDashboard(vm.Dashboard):
    """Custom Dashboard model."""

    def build(self):
        dashboard_build_obj = super().build()
        dashboard_build_obj.children.append(dcc.Store(id="data-store", storage_type="local"))
        dashboard_build_obj.children.append(dcc.Store(id="api-store", storage_type="local"))
        dashboard_build_obj.children.append(dcc.Store(id="outputs-store", storage_type="session"))
        return dashboard_build_obj


SUPPORTED_MODELS = [
    "gpt-4o-mini",
    "gpt-4",
    "gpt-4-turbo",
    "gpt-3.5-turbo",
    "gpt-4o",
]


plot_page = MyPage(
    id="vizro_ai_plot_page",
    title="Vizro AI - Plot",
    layout=vm.Layout(
        grid=[
            *[[0, 0, 2, 2]] * 6,
            [1, 1, 2, 2],
            [3, 3, 2, 2],
            [4, 4, 2, 2],
        ]
    ),
    components=[
        vm.Container(title="", components=[CodeClipboard(id="plot")]),
        UserPromptTextArea(
            id="text-area",
        ),
        vm.Graph(id="graph", figure=px.scatter(pd.DataFrame())),
        vm.Container(
            title="",
            layout=vm.Layout(grid=[[0], [1]], row_gap="0px"),
            components=[
                UserUpload(
                    id="data-upload",
                    actions=[
                        vm.Action(
                            function=data_upload_action(),
                            inputs=["data-upload.contents", "data-upload.filename"],
                            outputs=["data-store.data"],
                        ),
                        vm.Action(
                            function=display_filename(),
                            inputs=["data-store.data"],
                            outputs=["upload-message-id.children"],
                        ),
                    ],
                ),
                vm.Card(id="upload-message-id", text="Upload your data file (csv or excel)"),
            ],
        ),
        vm.Container(
            title="",
            layout=vm.Layout(grid=[[0, 0, 1, 1, -1, -1, -1, 2, 3]], row_gap="0px", col_gap="4px"),
            components=[
                vm.Button(
                    id="trigger-button",
                    text="Run VizroAI",
                    actions=[
                        vm.Action(
                            function=run_vizro_ai(),
                            inputs=[
                                "text-area.value",
                                "trigger-button.n_clicks",
                                "data-store.data",
                                "model-dropdown.value",
                                "api-store.data",
                            ],
                            outputs=["plot_code-markdown.children", "graph.figure", "outputs-store.data"],
                        ),
                    ],
                ),
                MyDropdown(options=SUPPORTED_MODELS, value="gpt-3.5-turbo", multi=False, id="model-dropdown"),
                vm.Button(id="open_canvas", text="Settings"),
                OffCanvas(id="offcanvas-id", options=["ChatOpenAI"], value="ChatOpenAI"),
            ],
        ),
    ],
)


dashboard = CustomDashboard(
    pages=[plot_page],
    navigation=vm.Navigation(
        nav_selector=vm.NavBar(
            items=[
                vm.NavLink(icon="robot_2", pages=["vizro_ai_plot_page"], label="Vizro-AI Plot"),
            ]
        )
    ),
)


# pure dash callbacks
@callback(
    [
        Output("plot_code-markdown", "children", allow_duplicate=True),
        Output("graph", "figure", allow_duplicate=True),
        Output("text-area", "value"),
        Output("upload-message-id", "children"),
    ],
    [Input("on_page_load_action_trigger_vizro_ai_plot_page", "data")],
    [State("outputs-store", "data")],
    prevent_initial_call="initial_duplicate",
)
def update_data(page_data, outputs_data):
    if not outputs_data:
        raise PreventUpdate

    ai_response = outputs_data["ai_response"]
    fig = json.loads(outputs_data["figure"])
    filename = f"Uploaded file name: '{outputs_data['filename']}'"
    prompt = outputs_data["prompt"]

    return ai_response, fig, prompt, filename


@callback(
    Output("offcanvas-id", "is_open"),
    Input("open_canvas", "n_clicks"),
    [State("offcanvas-id", "is_open")],
)
def toggle_offcanvas(n_clicks, is_open):
    return not is_open if n_clicks else is_open


@callback(
    [Output("api-store", "data"), Output("offcanvas-id_notification", "children")],
    [
        Input("offcanvas-id_api_key", "value"),
        Input("offcanvas-id_api_base", "value"),
        Input("offcanvas-id_save-secrets-id", "n_clicks"),
    ],
)
def save_secrets(api_key, api_base, n_clicks):
    if not n_clicks:
        raise PreventUpdate

    if api_key and api_base:
        return {"api_key": api_key, "api_base": api_base}, "Secrets saved!"


@callback(
    [Output("offcanvas-id_api_key", "type"), Output("offcanvas-id_api_base", "type")],
    Input("offcanvas-id_toggle-secrets-id", "value"),
)
def show_secrets(value):
    return ("text", "text") if value else ("password", "password")


Vizro().build(dashboard).run()
