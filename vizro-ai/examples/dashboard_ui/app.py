"""VizroAI UI dashboard configuration."""

import black
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from actions import data_upload_action, display_filename, run_vizro_ai, update_table
from components import (
    CodeClipboard,
    CustomDashboard,
    CustomImg,
    Icon,
    Modal,
    MyDropdown,
    OffCanvas,
    ToggleSwitch,
    UserPromptTextArea,
    UserUpload,
    custom_table,
)
from dash import Input, Output, State, callback, dcc, get_asset_url, html
from vizro import Vizro

vm.Container.add_type("components", UserUpload)
vm.Container.add_type("components", MyDropdown)
vm.Container.add_type("components", OffCanvas)
vm.Container.add_type("components", CodeClipboard)
vm.Container.add_type("components", Icon)
vm.Container.add_type("components", Modal)
vm.Container.add_type("components", ToggleSwitch)
vm.Container.add_type("components", CustomImg)

vm.Page.add_type("components", UserPromptTextArea)
vm.Page.add_type("components", UserUpload)
vm.Page.add_type("components", MyDropdown)
vm.Page.add_type("components", OffCanvas)
vm.Page.add_type("components", CodeClipboard)
vm.Page.add_type("components", Icon)
vm.Page.add_type("components", Modal)


SUPPORTED_MODELS = [
    "gpt-4o-mini",
    "gpt-4",
    "gpt-4-turbo",
    "gpt-3.5-turbo",
    "gpt-4o",
]


plot_page = vm.Page(
    id="vizro_ai_plot_page",
    title="Vizro-AI - effortlessly create interactive charts with Plotly",
    layout=vm.Layout(
        grid=[
            [3, 3, -1, 5],
            [3, 3, 2, 2],
            [1, 1, 2, 2],
            [4, 4, 2, 2],
            *[[0, 0, 2, 2]] * 6,
        ]
    ),
    components=[
        vm.Container(
            title="",
            components=[CodeClipboard(id="plot"), ToggleSwitch(id="toggle-id"), CustomImg(id="json-download")],
            layout=vm.Layout(
                grid=[*[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]] * 7, [-1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 2]],
                row_gap="12px",
                col_gap="12px",
            ),
        ),
        UserPromptTextArea(
            id="text-area-id",
        ),
        vm.Graph(id="graph-id", figure=px.scatter(pd.DataFrame())),
        vm.Container(
            title="",
            layout=vm.Layout(grid=[[1], [0], [2]], row_gap="0px", row_min_height="40px"),
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
                        vm.Action(
                            function=update_table(), inputs=["data-store-id.data"], outputs=["accordion-table.children"]
                        ),
                    ],
                ),
                vm.Card(id="upload-message-id", text="Upload your data file (csv or excel)"),
                vm.Figure(id="show-data-component", figure=custom_table(data_frame=pd.DataFrame())),
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
                            outputs=["plot-code-markdown.children", "graph-id.figure", "code-output-store-id.data"],
                        ),
                    ],
                ),
                MyDropdown(options=SUPPORTED_MODELS, value="gpt-4o-mini", multi=False, id="model-dropdown-id"),
                OffCanvas(id="settings", options=["OpenAI"], value="OpenAI"),
                # Modal(id="modal"),
            ],
        ),
        Icon(id="open-settings-id"),
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
    Output("download-json", "data"),
    Input("json-download-icon", "n_clicks"),
    [State("code-output-store-id", "data"), State("toggle-switch", "value")],
)
def download_json(n_clicks, data, value):
    """Callback for switching between vizro and plotly code."""
    if not data:
        return dash.no_update
    if not n_clicks:
        return dash.no_update

    figure_json = data["ai_outputs"]["vizro"]["fig"] if value else data["ai_outputs"]["plotly"]["fig"]
    file_name = "vizro_fig" if value else "plotly_fig"

    return dcc.send_string(figure_json, f"{file_name}.json")


app = Vizro().build(dashboard)
app.dash.layout.children.append(
    html.Div(
        [
            dbc.NavLink("Contact Vizro", href="https://github.com/mckinsey/vizro/issues"),
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
