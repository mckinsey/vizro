"""VizroAI UI dashboard configuration."""

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from components import CodeClipboard, InputForm, UserPromptTextArea, UserUpload
from dash import dcc
from vizro import Vizro
from vizro_ai_model import data_upload_action, run_vizro_ai, save_api_key

vm.Page.add_type("components", UserPromptTextArea)
vm.Page.add_type("components", InputForm)
vm.Page.add_type("components", vm.Dropdown)
vm.Page.add_type("components", UserUpload)

vm.Container.add_type("components", InputForm)
vm.Container.add_type("components", vm.Dropdown)
vm.Container.add_type("components", UserUpload)


vm.Container.add_type("components", CodeClipboard)
vm.Page.add_type("components", CodeClipboard)


SUPPORTED_MODELS = [
    "gpt-4-0613",
    "gpt-4",
    "gpt-4-1106-preview",
    "gpt-4-turbo",
    "gpt-4-turbo-2024-04-09",
    "gpt-4-turbo-preview",
    "gpt-4-0125-preview",
    "gpt-3.5-turbo-1106",
    "gpt-3.5-turbo-0125",
    "gpt-3.5-turbo",
    "gpt-4o-2024-05-13",
    "gpt-4o",
]


page = vm.Page(
    id="vizro_ai_page",
    title="Vizro AI",
    layout=vm.Layout(grid=[*[[0, 0, 2, 2]] * 6, [1, 1, 2, 2], [3, 3, 2, 2], [4, 4, 2, 2]]),
    components=[
        vm.Container(title="", components=[CodeClipboard()]),
        UserPromptTextArea(
            id="text-area",
        ),
        vm.Graph(id="graph", figure=px.scatter(pd.DataFrame())),
        UserUpload(
            id="data-upload",
            actions=[
                vm.Action(
                    function=data_upload_action(),
                    inputs=["data-upload.contents", "data-upload.filename"],
                    outputs=["data-store.data"],
                )
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
                            outputs=["code-markdown.children", "graph.figure"],
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
                InputForm(id="api-base", placeholder="API base"),
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
                    [0, -1],
                    [1, -1],
                    [2, -1],
                    *[[-1, -1]] * 2,
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
        dashboard_build_obj.children.append(dcc.Store(id="data-store"))
        dashboard_build_obj.children.append(dcc.Store(id="api-store", storage_type="session"))
        return dashboard_build_obj


dashboard = CustomDashboard(
    pages=[page, settings],
    navigation=vm.Navigation(
        nav_selector=vm.NavBar(
            items=[
                vm.NavLink(icon="robot_2", pages=["vizro_ai_page"], label="Vizro-AI"),
                vm.NavLink(icon="settings", pages=["settings_page"], label="Settings"),
            ]
        )
    ),
)


Vizro().build(dashboard).run()
