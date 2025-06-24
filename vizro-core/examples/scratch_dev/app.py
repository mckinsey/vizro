from time import sleep
from typing import Any

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm
import vizro.plotly.express as px
from charts import custom_scatter
from dash import html
from vizro import Vizro
from vizro.managers import data_manager, model_manager
from vizro.models.types import capture

data_manager["iris"] = px.data.iris()

dashboard_config = {
    "title": "Test dashboard",
    "pages": [
        {
            "title": "Page 1",
            "components": [
                # {"type": "card", "text": "Hello, world!"},
                # {
                #     "type": "graph",
                #     "figure": {
                #         "_target_": "scatter",
                #         "data_frame": "iris",
                #         "x": "sepal_length",
                #         "y": "sepal_width",
                #     },
                # },
                # {
                #     "type": "graph",
                #     "figure": {
                #         "_target_": "charts.custom_scatter",
                #         "data_frame": "iris",
                #         "x": "sepal_length",
                #         "y": "sepal_width",
                #     },
                # },
                # {
                #     "type": "graph",
                #     "figure": {
                #         "_target_": "__main__.custom_bar",
                #         "data_frame": "iris",
                #         "x": "sepal_length",
                #         "y": "sepal_width",
                #     },
                # },
                # {
                #     "type": "graph",
                #     "figure": {
                #         "_target_": "custom_bar2",
                #         "data_frame": "iris",
                #     },
                # },
                {"type": "ag_grid", "figure": {"_target_": "__main__.custom_grid", "data_frame": "iris"}},
                # {"type": "figure", "figure": {"_target_": "__main__.custom_kpi_card", "data_frame": "iris"}},
                {
                    "type": "button",
                    "text": "Export data",
                    "actions": [
                        {"function": {"_target_": "export_data"}},
                        {"function": {"_target_": "__main__.my_custom_action", "t": 5}},
                        {"function": {"_target_": "export_data", "file_format": "xlsx"}},
                    ],
                },
                # {"type": "ag_grid", "figure": {"_target_": "weird_grid", "data_frame": "iris"}},
            ],
        }
    ],
}


@capture("graph")
def custom_bar(data_frame: str, x: str, y: str):
    return go.Figure(data=[go.Bar(x=data_frame[x], y=data_frame[y])])


@capture("ag_grid")
def custom_grid(data_frame: pd.DataFrame) -> dag.AgGrid:
    defaults = {
        "columnDefs": [{"field": col} for col in data_frame.columns],
        "rowData": data_frame.to_dict("records"),
    }
    return dag.AgGrid(**defaults)


@capture("figure")
def custom_kpi_card(
    data_frame: pd.DataFrame,
) -> dbc.Card:
    """Creates a custom KPI card."""
    value = data_frame.info()

    header = dbc.CardHeader(
        [
            html.H4("Info", className="card-kpi-title"),
        ]
    )
    body = dbc.CardBody([value])
    return dbc.Card([header, body], class_name="card-kpi")


@capture("action")
def my_custom_action(t: int):
    sleep(t)


# dashboard = vm.Dashboard(
#     title="Test dashboard",
#     pages=[
#         vm.Page(
#             title="Page 1",
#             components=[
#                 vm.Card(text="Hello, world!"),
#                 vm.Graph(figure=px.scatter(data_frame="iris", x="sepal_length", y="sepal_width")),
#                 vm.Graph(figure=custom_scatter(data_frame="iris", x="sepal_length", y="sepal_width")),
#                 vm.AgGrid(figure=custom_grid(data_frame="iris")),
#             ],
#             controls=[vm.Filter(column="sepal_length")],
#         )
#     ],
# )


if __name__ == "__main__":
    dashboard = vm.Dashboard.model_validate(
        dashboard_config,
        context={"allowed_undefined_captured_callables": [("custom_bar2", "graph"), ("weird_grid", "ag_grid", 3)]},
    )
    # print(dashboard._to_python())
    # config = dashboard.model_dump(exclude_unset=True)
    # print(config)
    # print("-" * 100)
    # model_manager._clear()
    # dashboard2 = vm.Dashboard.model_validate(config)
    # print(dashboard2._to_python())
    # app = Vizro().build(dashboard)

    # app.run(debug=True)

    # What I ultimately want:

    # - import path is the clean and normal way to define custom additions to vizro, ie json in .json, python in .py
    # - serializing a Dashboard object should be possible with external captured callables
    #   - for pre-defined callables (like px or vizro functions), this would be just normal json
    #   - for user-defined callables, LETS SEE
    # - instantiation:

    # ag_grid = {
    #     "type": "ag_grid",
    #     "figure": {
    #         "_target_": "no_import_grid",
    #         "data_frame": "iris",
    #     },
    # }

    # model = vm.AgGrid.model_validate(
    #     ag_grid, context={"allowed_undefined_captured_callables": [("no_import_grid", "ag_grid")]}
    # )

    # print(model._to_python())
