"""VizroAI UI dashboard configuration."""

import json

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from components import (
    CodeClipboard,
    InputForm,
    MyCard,
    MyDropdown,
    MyPage,
    OffCanvas,
    Switch,
    UserPromptTextArea,
    UserUpload,
)
from custom_actions import data_upload_action, display_filename, run_vizro_ai, run_vizro_ai_dashboard
from dash import Input, Output, State, callback, dcc
from dash.exceptions import PreventUpdate
from vizro import Vizro

vm.Container.add_type("components", InputForm)
vm.Container.add_type("components", vm.Dropdown)
vm.Container.add_type("components", UserUpload)
vm.Container.add_type("components", Switch)
vm.Container.add_type("components", MyCard)
vm.Container.add_type("components", MyDropdown)
vm.Container.add_type("components", OffCanvas)

MyPage.add_type("components", UserPromptTextArea)
MyPage.add_type("components", InputForm)
MyPage.add_type("components", vm.Dropdown)
MyPage.add_type("components", UserUpload)
MyPage.add_type("components", MyCard)
MyPage.add_type("components", MyDropdown)
MyPage.add_type("components", OffCanvas)
MyPage.add_type("components", CodeClipboard)
MyPage.add_type("components", CodeClipboard)

vm.Container.add_type("components", CodeClipboard)
vm.Page.add_type("components", CodeClipboard)
vm.Page.add_type("components", Switch)


class CustomDashboard(vm.Dashboard):
    """Custom Dashboard model."""

    def build(self):
        dashboard_build_obj = super().build()
        dashboard_build_obj.children.append(dcc.Store(id="data-store", storage_type="local"))
        dashboard_build_obj.children.append(dcc.Store(id="api-store", storage_type="local"))
        dashboard_build_obj.children.append(dcc.Store(id="outputs-store", storage_type="session"))
        dashboard_build_obj.children.append(dcc.Store(id="dashboard-data-store", storage_type="local"))
        dashboard_build_obj.children.append(dcc.Store(id="dashboard-api-store", storage_type="local"))
        dashboard_build_obj.children.append(dcc.Store(id="dashboard-outputs-store", storage_type="session"))
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


dashboard_page = MyPage(
    id="vizro_ai_dashboard_page",
    title="Vizro AI - Dashboard",
    layout=vm.Layout(
        grid=[
            *[[0, 0, 0, 0]] * 6,
            [1, 1, 1, 1],
            [2, 2, 2, 2],
            [3, 3, 3, 3],
        ]
    ),
    components=[
        vm.Container(title="", components=[CodeClipboard(id="dashboard")]),
        UserPromptTextArea(
            id="dashboard-text-area",
        ),
        vm.Container(
            title="",
            layout=vm.Layout(grid=[[0], [1]], row_gap="0px"),
            components=[
                UserUpload(
                    id="dashboard-data-upload",
                    actions=[
                        vm.Action(
                            function=data_upload_action(),
                            inputs=["dashboard-data-upload.contents", "dashboard-data-upload.filename"],
                            outputs=["dashboard-data-store.data"],
                        ),
                        vm.Action(
                            function=display_filename(),
                            inputs=["dashboard-data-store.data"],
                            outputs=["dashboard-upload-message-id.children"],
                        ),
                    ],
                ),
                vm.Card(id="dashboard-upload-message-id", text="Upload your data files (csv or excel)"),
            ],
        ),
        vm.Container(
            title="",
            layout=vm.Layout(grid=[[0, 0, 1, 1, -1, -1, -1, 2, 3]], row_gap="0px", col_gap="4px"),
            components=[
                vm.Button(
                    id="dashboard-trigger-button",
                    text="Run VizroAI",
                    actions=[
                        vm.Action(
                            function=run_vizro_ai_dashboard(),
                            inputs=[
                                "dashboard-text-area.value",
                                "dashboard-trigger-button.n_clicks",
                                "dashboard-data-store.data",
                                "dashboard-model-dropdown.value",
                                "dashboard-api-store.data",
                            ],
                            outputs=["dashboard_code-markdown.children", "dashboard-outputs-store.data"],
                        ),
                    ],
                ),
                MyDropdown(options=SUPPORTED_MODELS, value="gpt-3.5-turbo", multi=False, id="dashboard-model-dropdown"),
                vm.Button(id="dashboard-open_canvas", text="Settings"),
                OffCanvas(id="dashboard-offcanvas-id", options=["ChatOpenAI"], value="ChatOpenAI"),
            ],
        ),
    ],
)


dashboard = CustomDashboard(
    pages=[plot_page, dashboard_page],
    navigation=vm.Navigation(
        nav_selector=vm.NavBar(
            items=[
                vm.NavLink(icon="robot_2", pages=["vizro_ai_plot_page"], label="Vizro-AI Plot"),
                vm.NavLink(icon="dashboard", pages=["vizro_ai_dashboard_page"], label="Vizro-AI Dashboard"),
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


# dashboard callbacks


@callback(
    [Output("dashboard-api-store", "data"), Output("dashboard-offcanvas-id_notification", "children")],
    [
        Input("dashboard-offcanvas-id_api_key", "value"),
        Input("dashboard-offcanvas-id_api_base", "value"),
        Input("dashboard-offcanvas-id_save-secrets-id", "n_clicks"),
    ],
)
def save_dashboard_secrets(api_key, api_base, n_clicks):
    if not n_clicks:
        raise PreventUpdate

    if api_key and api_base:
        return {"api_key": api_key, "api_base": api_base}, "Secrets saved!"


@callback(
    [Output("dashboard-offcanvas-id_api_key", "type"), Output("dashboard-offcanvas-id_api_base", "type")],
    Input("offcanvas-id_toggle-secrets-id", "value"),
)
def show_secrets(value):
    return ("text", "text") if value else ("password", "password")


@callback(
    Output("dashboard-offcanvas-id", "is_open"),
    Input("dashboard-open_canvas", "n_clicks"),
    [State("dashboard-offcanvas-id", "is_open")],
)
def toggle_offcanvas(n_clicks, is_open):
    return not is_open if n_clicks else is_open


@callback(
    [
        Output("dashboard_code-markdown", "children", allow_duplicate=True),
        Output("dashboard-text-area", "value"),
        Output("dashboard-upload-message-id", "children"),
    ],
    [Input("on_page_load_action_trigger_vizro_ai_plot_dashboard", "data")],
    [State("dashboard-outputs-store", "data")],
    prevent_initial_call="initial_duplicate",
)
def update_data(page_data, outputs_data):
    if not outputs_data:
        raise PreventUpdate

    ai_response = outputs_data["ai_response"]
    filename = f"Uploaded file name: '{outputs_data['filename']}'"
    prompt = outputs_data["prompt"]

    return ai_response, prompt, filename


Vizro().build(dashboard).run()
