"""VizroAI dashboard UI configuration."""

import json
import subprocess

import dash_bootstrap_components as dbc
import vizro.models as vm
from actions import data_upload_action, display_filename
from components import (
    CodeClipboard,
    CustomDashboard,
    Icon,
    Modal,
    MyDropdown,
    MyPage,
    OffCanvas,
    UserPromptTextArea,
    UserUpload,
)
from dash import Input, Output, State, callback, get_asset_url, html
from dash.exceptions import PreventUpdate
from vizro import Vizro

SUPPORTED_MODELS = [
    "gpt-4o-mini",
    "gpt-4",
    "gpt-4-turbo",
    "gpt-3.5-turbo",
    "gpt-4o",
]
vm.Container.add_type("components", UserUpload)
vm.Container.add_type("components", MyDropdown)
vm.Container.add_type("components", OffCanvas)
vm.Container.add_type("components", CodeClipboard)
vm.Container.add_type("components", Icon)
vm.Container.add_type("components", Modal)

MyPage.add_type("components", UserPromptTextArea)
MyPage.add_type("components", UserUpload)
MyPage.add_type("components", MyDropdown)
MyPage.add_type("components", OffCanvas)
MyPage.add_type("components", CodeClipboard)
MyPage.add_type("components", Icon)
vm.Container.add_type("components", Modal)

dashboard_page = MyPage(
    id="vizro_ai_dashboard_page",
    title="Vizro AI - Dashboard",
    layout=vm.Layout(
        grid=[[2, 2, 0, 0, 0], [1, 1, 0, 0, 0], [1, 1, 0, 0, 0], [1, 1, 0, 0, 0], [1, 1, 0, 0, 0], [3, 3, 0, 0, 0]]
    ),
    components=[
        vm.Container(title="", components=[CodeClipboard(id="dashboard")], id="clipboard-container"),
        UserPromptTextArea(id="dashboard-text-area", placeholder="Describe the dashboard you want to create."),
        vm.Container(
            title="",
            layout=vm.Layout(grid=[[0], [1]], row_gap="0px"),
            components=[
                vm.Card(id="dashboard-upload-message-id", text="Upload your data files (csv or excel)"),
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
            ],
        ),
        vm.Container(
            title="",
            layout=vm.Layout(
                grid=[[3, -1, -1, -1, -1, -1, 1, 1, 0, 0], [-1, -1, -1, -1, -1, -1, -1, -1, 2, 2]],
                row_gap="0px",
                col_gap="4px",
            ),
            components=[
                vm.Button(
                    id="dashboard-trigger-button",
                    text="Run VizroAI",
                ),
                MyDropdown(options=SUPPORTED_MODELS, value="gpt-4o-mini", multi=False, id="dashboard-model-dropdown"),
                Icon(id="open-settings-id"),
                OffCanvas(id="dashboard-settings", options=["OpenAI"], value="OpenAI"),
                # Modal(id="modal"),
            ],
        ),
    ],
)

dashboard = CustomDashboard(pages=[dashboard_page])


@callback(
    Output("dashboard-settings-api-key", "type"),
    Input("dashboard-settings-api-key-toggle", "value"),
)
def show_api_key(value):
    """Callback to show api key."""
    return "text" if value else "password"


@callback(
    Output("dashboard-settings-api-base", "type"),
    Input("dashboard-settings-api-base-toggle", "value"),
)
def show_api_base(value):
    """Callback to show api base."""
    return "text" if value else "password"


@callback(
    Output("dashboard-settings", "is_open"),
    Input("open-settings-id", "n_clicks"),
    [State("dashboard-settings", "is_open")],
)
def open_settings(n_clicks, is_open):
    """Callback for opening and closing offcanvas settings component."""
    return not is_open if n_clicks else is_open


@callback(
    Output("dashboard-code-markdown", "children"),
    [
        State("dashboard-text-area", "value"),
        State("dashboard-model-dropdown", "value"),
        State("dashboard-settings-api-key", "value"),
        State("dashboard-settings-api-base", "value"),
        Input("dashboard-trigger-button", "n_clicks"),
        State("dashboard-data-store", "data"),
        State("dashboard-settings-dropdown", "value"),
    ],
)
def run_script(user_prompt, model, api_key, api_base, n_clicks, data, vendor):  # noqa: PLR0913
    """Callback for triggering subprocess that run vizro-ai."""
    data = json.dumps(data)
    if n_clicks is None:
        raise PreventUpdate
    else:
        process = subprocess.Popen(
            [
                "python",
                "run_vizro_ai.py",
                "--arg1",
                f"{user_prompt}",
                "--arg2",
                f"{model}",
                "--arg3",
                f"{api_key}",
                "--arg4",
                f"{api_base}",
                "--arg5",
                f"{n_clicks}",
                "--arg6",
                f"{vendor}",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout_data, stderr_data = process.communicate(input=data)
        if stdout_data:
            start_index = stdout_data.find("```")
            return stdout_data[start_index:]
        return stderr_data


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


server = app.dash.server
if __name__ == "__main__":
    app.run()
