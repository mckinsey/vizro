"""Demo app."""

# TODO: To run this program:
#  1. upload px.data.gapminder() data to first page upload component
#  2. create idea_s_demo/data/output_data folder

import logging
import base64
import pandas as pd
import io

from dash import callback, exceptions, Output, Input
from pathlib import Path
from time import sleep

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data, filter_interaction
from vizro.tables import dash_ag_grid, dash_data_table
from vizro.managers import data_manager
from vizro.models.types import capture

from custom_components import LoadingSpinner, LogsInterval, MyButton, MyCard, Upload


vm.Container.add_type("components", Upload)
vm.Container.add_type("components", LoadingSpinner)
vm.Container.add_type("components", MyButton)
vm.Container.add_type("components", MyCard)
vm.Container.add_type("components", LogsInterval)

vm.Page.add_type("controls", vm.Button)

columnDefs = [
    {"field": "country"},
    {"field": "year"},
    {"field": "lifeExp", "cellDataType": "numeric"},
    {"field": "gdpPercap", "cellDataType": "dollar"},
    {"field": "pop", "cellDataType": "numeric"},
]

# LOGGER -----------------------------------------------------------------------
# TODO: Adjust the interval to the desired value for the logs to be refreshed and displayed on the page.
LOGS_INTERVAL_IN_SECONDS = 1


def create_file_logger(logger_name, file_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(file_name)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


script_1_logger = create_file_logger("script_1_logger", "logs/file_1.log")
script_2_logger = create_file_logger("script_2_logger", "logs/file_2.log")


# DATA ----------------------------------------------------------------------->
DATA_DIR = Path.cwd().joinpath('data')


def _load_data(file_path):
    if file_path.exists():
        return pd.read_csv(file_path)
    print("Using default data, file path might be incorrect")
    return px.data.gapminder()


def page_2_load_data():
    return _load_data(DATA_DIR.joinpath("output_data/script_1_result_data.csv"))


def page_3_load_data():
    return _load_data(DATA_DIR.joinpath("output_data/script_2_result_data.csv"))


data_manager["page_2_data"] = page_2_load_data
data_manager["page_3_data"] = page_3_load_data


# ACTIONS ----------------------------------------------------------------------->


@capture("action")
def upload_data_action(contents, filename):
    if not contents:
        raise exceptions.PreventUpdate

    return (
        f"Uploaded file name: '{filename}'",
        False,
        False,
        "File is uploaded. Run the script.",
        "File is uploaded. Run the script.",
    )


@capture("action")
def pre_script_action():
    return "Script status: Pending", True, False


# This could be any algorithm like ML, DL, etc.
@capture("action")
def script_action(contents, filename, script_id, filter_year):
    # LOGS
    logger = script_1_logger if script_id == 1 else script_2_logger

    with open(f"logs/file_{script_id}.log", "w") as f:
        f.write("")

    logger.info(f"Script {script_id} started.")
    for i in range(5):
        logger.info(f"Script progress - {i * 25}%")
        sleep(LOGS_INTERVAL_IN_SECONDS)

    # READ DATA
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    data_io = io.StringIO(decoded.decode('utf-8'))
    df = pd.read_csv(data_io)

    # HEAVY OPERATION
    # This simple filtering represents the heavy operation that could be done in the script.
    df = df[df["year"] == filter_year]

    # WRITE DATA
    df.to_csv(DATA_DIR.joinpath(f"output_data/script_{script_id}_result_data.csv"), index=False)

    # LOGS
    logger.info(f"Script {script_id} finished.")
    sleep(LOGS_INTERVAL_IN_SECONDS)

    return "", "Script status: Done", False, True, {"display": "block"}


@callback(
    Output("tab_1_card_logs_id", "children", allow_duplicate=True),
    Input("tab_1_logs_interval_id", "n_intervals"),
    prevent_initial_call=True
)
def page_1_get_logs_from_file(n_intervals):
    with open("logs/file_1.log", "r") as f:
        logs = f.readlines()

    return '\n\n'.join(logs)


@callback(
    Output("tab_2_card_logs_id", "children", allow_duplicate=True),
    Input("tab_2_logs_interval_id", "n_intervals"),
    prevent_initial_call=True
)
def page_2_get_logs_from_file(n_intervals):
    with open("logs/file_2.log", "r") as f:
        logs = f.readlines()

    return '\n\n'.join(logs)


# PAGES ----------------------------------------------------------------------->

def get_run_script_component(script_id, nav_to_page, filter_year):
    return vm.Container(
        title=f"Script {script_id}",
        layout=vm.Layout(
            grid=[
                [0, 0, 0, 0],
                [1, 1, 1, 1],
                [1, 1, 1, 1],
                [2, 2, 2, 3]
            ]
        ),
        components=[
            vm.Container(
                title=f"Run Script {script_id}",
                layout=vm.Layout(
                    grid=[
                        [0, 0, 0],
                        [1, 2, -1],
                    ],
                    row_gap="0px",
                    col_gap="40px",
                ),
                components=[
                    vm.Card(id=f"tab_{script_id}_upload_card_id", text="Upload your data to run the script."),
                    MyButton(
                        id=f"tab_{script_id}_run_script_button_id",
                        text=f"Run Script {script_id}",
                        actions=[
                            vm.Action(
                                function=pre_script_action(),
                                outputs=[
                                    f"tab_{script_id}_upload_card_id.children",
                                    f"tab_{script_id}_run_script_button_id.disabled",
                                    f"tab_{script_id}_logs_interval_id.disabled",
                                ]
                            ),
                            vm.Action(
                                function=script_action(script_id=script_id, filter_year=filter_year),
                                inputs=[
                                    "page_1_upload_id.contents",
                                    "page_1_upload_id.filename",
                                ],
                                outputs=[
                                    f"tab_{script_id}_loading_spinner.children",
                                    f"tab_{script_id}_upload_card_id.children",
                                    f"tab_{script_id}_run_script_button_id.disabled",
                                    f"tab_{script_id}_logs_interval_id.disabled",
                                    f"tab_{script_id}_nav_card_id_outer_div.style"
                                ]
                            ),
                        ]
                    ),
                    LoadingSpinner(id=f"tab_{script_id}_loading_spinner"),
                ],
            ),
            vm.Container(
                title="Logs Section",
                components=[
                    vm.Card(id=f"tab_{script_id}_card_logs_id", text="Script logs:"),
                ],
            ),
            LogsInterval(id=f"tab_{script_id}_logs_interval_id", interval=1000 * LOGS_INTERVAL_IN_SECONDS),
            MyCard(
                id=f"tab_{script_id}_nav_card_id",
                href=nav_to_page,
                text=(
                    f"""
                        ### Click Here  &#10132;

                        to see the results on the '{nav_to_page}'.
                    """
                ),
            ),
        ],
    )


page_1 = vm.Page(
    id="page-1",
    title="Data processing",
    layout=vm.Layout(grid=[[0], [1], [1], [1]]),
    components=[
        vm.Container(
            title="",
            layout=vm.Layout(
                grid=[
                    [0, -1, -1, -1],
                    [1, -1, -1, -1],
                    [1, -1, -1, -1],
                ],
                row_gap="0px",
            ),
            components=[
                vm.Card(id="page_1_upload_card_id", text="Upload your data."),
                Upload(
                    id="page_1_upload_id",
                    title="Upload Data",
                    actions=[
                        vm.Action(
                            function=upload_data_action(),
                            inputs=[
                                "page_1_upload_id.contents",
                                "page_1_upload_id.filename",
                            ],
                            outputs=[
                                "page_1_upload_card_id.children",
                                "tab_1_run_script_button_id.disabled",
                                "tab_2_run_script_button_id.disabled",
                                "tab_1_upload_card_id.children",
                                "tab_2_upload_card_id.children",
                            ]
                        )
                    ],
                ),
            ],
        ),
        vm.Tabs(
            tabs=[
                get_run_script_component(script_id=1, nav_to_page="page-2", filter_year=1952),
                get_run_script_component(script_id=2, nav_to_page="page-3", filter_year=2007),
            ]
        ),
    ],
)


def get_results_page(page_id, title, data_id):
    return vm.Page(
        id=page_id,
        title=title,
        layout=vm.Layout(grid=[[0, 1], [2, 2]]),
        components=[
            vm.Graph(
                id=f"{page_id}_graph_1_id",
                figure=px.box(
                    data_id,
                    title="Graph 1",
                    x="continent",
                    y="gdpPercap",
                    color="continent",
                    custom_data=["continent"]
                ),
                actions=[
                    vm.Action(function=filter_interaction(targets=[f"{page_id}_graph_2_id"]))
                ]
            ),
            vm.Graph(
                id=f"{page_id}_graph_2_id",
                figure=px.scatter(
                    data_id,
                    title="Graph 2",
                    x="lifeExp",
                    y="gdpPercap",
                    color="continent",
                    size="pop",
                    hover_data=["country"],
                ),
            ),
            vm.Table(
                id=f"{page_id}_table_3_id",
                title="Results table",
                figure=dash_data_table(data_frame=data_id, page_size=7),
            ),
        ],
        controls=[
            vm.Parameter(
                targets=[f"{page_id}_graph_1_id.y", f"{page_id}_graph_2_id.y"],
                selector=vm.Dropdown(
                    title="Select Y-axis",
                    options=[
                        {"label": "GDP per Capita", "value": "gdpPercap"},
                        {"label": "Life Expectancy", "value": "lifeExp"},
                        {"label": "Population", "value": "pop"},
                    ],
                    value="gdpPercap",
                    multi=False
                ),
            ),
            vm.Filter(column="continent"),
            vm.Button(
                text="Export Data",
                actions=[vm.Action(function=export_data(targets=[f"{page_id}_table_3_id"]))]
            )
        ]
    )


page_2 = get_results_page("page-2", "Results for 1952", "page_2_data")
page_3 = get_results_page("page-3", "Results for 2007", "page_3_data")

dashboard = vm.Dashboard(pages=[page_1, page_2, page_3])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
