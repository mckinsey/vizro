"""Demo app."""

import vizro.models as vm
import vizro.plotly.express as px
from custom_components import LoadingSpinner, LogsInterval, MyButton, MyCard, Upload
from vizro import Vizro
from vizro.tables import dash_ag_grid, dash_data_table

df = px.data.gapminder().query("year == 2007")

vm.Page.add_type("components", LogsInterval)
vm.Page.add_type("components", MyCard)

vm.Page.add_type("controls", vm.Card)
vm.Page.add_type("controls", vm.Button)
vm.Page.add_type("controls", LoadingSpinner)
vm.Page.add_type("controls", MyButton)

vm.Container.add_type("components", Upload)
vm.Container.add_type("components", LoadingSpinner)
vm.Container.add_type("components", MyButton)
vm.Container.add_type("components", MyCard)
vm.Container.add_type("components", LogsInterval)

columnDefs = [
    {"field": "country"},
    {"field": "year"},
    {"field": "lifeExp", "cellDataType": "numeric"},
    {"field": "gdpPercap", "cellDataType": "dollar"},
    {"field": "pop", "cellDataType": "numeric"},
]

page_1 = vm.Page(
    id="page-1",
    title="Upload Data",
    layout=vm.Layout(grid=[[0], [1], [1], [1]]),
    components=[
        vm.Container(
            title="",
            layout=vm.Layout(
                grid=[
                    *[[0, 2, 2, 2]] * 2,
                    *[[1, 2, 2, 2]] * 4,
                ],
                row_gap="0px",
            ),
            components=[
                vm.Card(id="page_1_upload_card_id", text="Upload your data."),
                Upload(
                    id="page_1_upload_id",
                    title="Upload Data",
                    actions=[],
                ),
                vm.AgGrid(
                    id="page_1_hidden_table",
                    figure=dash_ag_grid(
                        data_frame=df.head(3),
                        columnDefs=columnDefs,
                        dashGridOptions={"rowSelection": "single"},
                    ),
                ),
            ],
        ),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Script 1",
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
                            title="Run Script 1",
                            layout=vm.Layout(
                                grid=[
                                    [0, 0, 0],
                                    [1, 2, -1],
                                ],
                                row_gap="0px",
                                col_gap="40px",
                            ),
                            components=[
                                vm.Card(id="tab_1_upload_card_id", text="Upload your data to run the script."),
                                MyButton(id="tab_1_run_script_button_id", text="Run Script 1"),
                                LoadingSpinner(id="page_2_loading_spinner"),
                            ],
                        ),
                        vm.Container(
                            title="Logs Section",
                            components=[
                                vm.Card(id="tab_1_card_logs_id", text="Script logs:"),
                            ],
                        ),
                        LogsInterval(id="tab_1_logs_interval_id", interval=1000),
                        MyCard(
                            id="tab_1_nav_card_id",
                            href="page-2",
                            text=(
                                """
                                    ### Click Here  &#10132;

                                    to see the results on the next page.
                                """
                            ),
                        ),
                    ],
                ),
                vm.Container(
                    title="Script 2",
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
                            title="Run Script 2",
                            layout=vm.Layout(
                                grid=[
                                    [0, 0, 0],
                                    [1, 2, -1],
                                ],
                                row_gap="0px",
                                col_gap="40px",
                            ),
                            components=[
                                vm.Card(id="tab_2_upload_card_id", text="Upload your data to run the script."),
                                MyButton(id="tab_2_run_script_button_id", text="Run Script 2"),
                                LoadingSpinner(id="tab_2_loading_spinner"),
                            ],
                        ),
                        vm.Container(
                            title="Logs Section",
                            components=[
                                vm.Card(id="tab_2_card_logs_id", text="Script logs:"),
                            ],
                        ),
                        LogsInterval(id="tab_2_logs_interval_id", interval=1000),
                        MyCard(
                            id="tab_2_nav_card_id",
                            href="page-3",
                            text=(
                                """
                                    ### Click Here  &#10132;

                                    to see the results on the next page.
                                """
                            ),
                        ),
                    ],
                ),
            ]
        ),
    ],
)

page_2 = vm.Page(
    id="page-2",
    title="Process Results",
    layout=vm.Layout(grid=[[0, 1], [2, 2]]),
    components=[
        vm.Graph(
            id="page-2-graph-1-id",
            figure=px.bar(
                df,
                title="Graph 1",
                x="continent",
                y="lifeExp",
                color="continent",
            ),
        ),
        vm.Graph(
            id="page-2-graph-2-id",
            figure=px.box(
                df,
                title="Graph 2",
                x="continent",
                y="lifeExp",
                color="continent",
            ),
        ),
        vm.Table(
            id="page-2-table-3-id",
            title="Results table",
            figure=dash_data_table(data_frame=df, page_size=7),
        ),
    ],
)

page_3 = vm.Page(
    id="page-3",
    title="Process Results 2",
    layout=vm.Layout(grid=[[0, 1], [2, 2]]),
    components=[
        vm.Graph(
            id="page-3-graph-1-id",
            figure=px.bar(
                df,
                title="Graph 1",
                x="continent",
                y="lifeExp",
                color="continent",
            ),
        ),
        vm.Graph(
            id="page-3-graph-2-id",
            figure=px.box(
                df,
                title="Graph 2",
                x="continent",
                y="lifeExp",
                color="continent",
            ),
        ),
        vm.Table(
            id="page-3-table-3-id",
            title="Results table",
            figure=dash_data_table(data_frame=df, page_size=7),
        ),
    ],
)


dashboard = vm.Dashboard(pages=[page_1, page_2, page_3])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
