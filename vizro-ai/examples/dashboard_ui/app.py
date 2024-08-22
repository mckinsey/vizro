"""VizroAI UI dashboard configuration."""

import pandas as pd
import plotly.io as pio
import vizro.models as vm
import vizro.plotly.express as px
from components import CodeClipboard, InputForm, MyCard, Switch, UserPromptTextArea, UserUpload
from custom_actions import data_upload_action, run_vizro_ai, save_api_key, toggle_api_key_visibility, upload_data_action
from dash import Input, Output, State, callback, dcc
from dash.exceptions import PreventUpdate
from vizro import Vizro
from vizro.charts._charts_utils import _DashboardReadyFigure

vm.Page.add_type("components", UserPromptTextArea)
vm.Page.add_type("components", InputForm)
vm.Page.add_type("components", vm.Dropdown)
vm.Page.add_type("components", UserUpload)
vm.Page.add_type("components", MyCard)

vm.Container.add_type("components", InputForm)
vm.Container.add_type("components", vm.Dropdown)
vm.Container.add_type("components", UserUpload)
vm.Container.add_type("components", Switch)
vm.Container.add_type("components", MyCard)


vm.Container.add_type("components", CodeClipboard)
vm.Page.add_type("components", CodeClipboard)
vm.Page.add_type("components", Switch)


SUPPORTED_MODELS = [
    "gpt-4o-mini",
    "gpt-4",
    "gpt-4-turbo",
    "gpt-3.5-turbo",
    "gpt-4o",
]


page = vm.Page(
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
                MyCard(id="upload-message-id", text="Upload your data file (csv or excel)"),
            ],
        ),
        vm.Container(
            title="",
            layout=vm.Layout(grid=[[0, 1, -1, -1]], row_gap="0px", col_gap="4px"),
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
                vm.Dropdown(options=SUPPORTED_MODELS, value="gpt-3.5-turbo", multi=False, id="model-dropdown"),
            ],
        ),
    ],
)

settings = vm.Page(
    id="settings-page",
    title="Settings",
    components=[
        vm.Container(
            title="",
            components=[
                InputForm(id="api-key", placeholder="API key"),
                Switch(
                    id="api-key-switch",
                    actions=[
                        vm.Action(
                            function=toggle_api_key_visibility(),
                            inputs=["api-key-switch.checked"],
                            outputs=["api-key.type"],
                        )
                    ],
                ),
                InputForm(id="api-base", placeholder="API base"),
                Switch(
                    id="api-base-switch",
                    actions=[
                        vm.Action(
                            function=toggle_api_key_visibility(),
                            inputs=["api-base-switch.checked"],
                            outputs=["api-base.type"],
                        )
                    ],
                ),
                vm.Button(
                    id="save-button",
                    text="Save",
                    actions=[
                        vm.Action(
                            function=save_api_key(),
                            inputs=["api-key.value", "api-base.value", "save-button.n_clicks"],
                            outputs=["api-store.data"],
                        )
                    ],
                ),
            ],
            layout=vm.Layout(
                grid=[
                    [0, 1, -1],
                    [2, 3, -1],
                    [4, -1, -1],
                    *[[-1, -1, -1]] * 2,
                ]
            ),
        )
    ],
    layout=vm.Layout(
        grid=[
            [0, 0, -1, -1],
            *[[-1, -1, -1, -1]] * 2,
        ]
    ),
)


class CustomDashboard(vm.Dashboard):
    """Custom Dashboard model."""

    def build(self):
        dashboard_build_obj = super().build()
        dashboard_build_obj.children.append(dcc.Store(id="data-store", storage_type="session"))
        dashboard_build_obj.children.append(dcc.Store(id="api-store", storage_type="session"))
        dashboard_build_obj.children.append(dcc.Store(id="outputs-store", storage_type="session"))
        return dashboard_build_obj


dashboard = CustomDashboard(
    pages=[page, settings],
    navigation=vm.Navigation(
        nav_selector=vm.NavBar(
            items=[
                vm.NavLink(icon="robot_2", pages=["vizro_ai_page"], label="Vizro-AI"),
                vm.NavLink(icon="settings", pages=["settings-page"], label="Settings"),
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
    figure = outputs_data["figure"]

    fig = pio.from_json(figure)
    fig.__class__ = _DashboardReadyFigure
    file_name = outputs_data["filename"]
    filename = f"Uploaded file name: '{file_name}'"
    prompt = outputs_data["prompt"]
    return ai_response, figure, prompt, filename


Vizro().build(dashboard).run()
