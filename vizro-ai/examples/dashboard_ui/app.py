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
from custom_actions import data_upload_action, run_vizro_ai, upload_data_action
from dash import Input, Output, State, callback, dcc
from dash.exceptions import PreventUpdate
from vizro import Vizro

vm.Page.add_type("components", UserPromptTextArea)
vm.Page.add_type("components", InputForm)
vm.Page.add_type("components", vm.Dropdown)
vm.Page.add_type("components", UserUpload)
vm.Page.add_type("components", MyCard)
vm.Page.add_type("components", MyDropdown)
vm.Page.add_type("components", OffCanvas)

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
        dashboard_build_obj.children.append(dcc.Store(id="data-store", storage_type="session"))
        dashboard_build_obj.children.append(dcc.Store(id="api-store", storage_type="session"))
        dashboard_build_obj.children.append(dcc.Store(id="outputs-store", storage_type="session"))
        return dashboard_build_obj


SUPPORTED_MODELS = [
    "gpt-4o-mini",
    "gpt-4",
    "gpt-4-turbo",
    "gpt-3.5-turbo",
    "gpt-4o",
]


page = MyPage(
    id="vizro_ai_page",
    title="Vizro AI",
    layout=vm.Layout(
        grid=[
            *[[0, 0, 2, 2]] * 6,
            [1, 1, 2, 2],
            [3, 3, 2, 2],
            [4, 4, 2, 2],
        ]
    ),
    components=[
        vm.Container(title="", components=[CodeClipboard()]),
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
                            function=upload_data_action(),
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
                            outputs=["code-markdown.children", "graph.figure", "outputs-store.data"],
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
    pages=[page],
    navigation=vm.Navigation(
        nav_selector=vm.NavBar(
            items=[
                vm.NavLink(icon="robot_2", pages=["vizro_ai_page"], label="Vizro-AI"),
            ]
        )
    ),
)


# pure dash callback
@callback(
    [
        Output("code-markdown", "children", allow_duplicate=True),
        Output("graph", "figure", allow_duplicate=True),
        Output("text-area", "value"),
        Output("upload-message-id", "children"),
    ],
    [Input("on_page_load_action_trigger_vizro_ai_page", "data")],
    [State("outputs-store", "data")],
    prevent_initial_call="initial_duplicate",
)
def update_data(page_data, outputs_data):
    if not outputs_data:
        raise PreventUpdate

    ai_response = outputs_data["ai_response"]
    stored_fig = outputs_data["figure"]
    fig = json.loads(stored_fig)

    file_name = outputs_data["filename"]
    filename = f"Uploaded file name: '{file_name}'"
    prompt = outputs_data["prompt"]
    return ai_response, fig, prompt, filename


@callback(
    Output("offcanvas-id", "is_open"),
    Input("open_canvas", "n_clicks"),
    [State("offcanvas-id", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open


@callback(
    [Output("api-store", "data"), Output("notification", "children")],
    [
        Input("offcanvas-id_api_key", "value"),
        Input("offcanvas-id_api_base", "value"),
        Input("save-secrets-id", "n_clicks"),
    ],
)
def save_secrets(api_key, api_base, n_clicks):
    if n_clicks:
        if api_key and api_base:
            return {"api_key": api_key, "api_base": api_base}, "Secrets saved!"


Vizro().build(dashboard).run()
