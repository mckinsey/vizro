from typing import Any

import dash_ag_grid as dag
import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm
import vizro.plotly.express as px
from charts import custom_scatter
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
                {"type": "card", "text": "Hello, world!"},
                {
                    "type": "graph",
                    "figure": {
                        "_target_": "scatter",
                        "data_frame": "iris",
                        "x": "sepal_length",
                        "y": "sepal_width",
                    },
                },
                {
                    "type": "graph",
                    "figure": {
                        "_target_": "charts.custom_scatter",
                        "data_frame": "iris",
                        "x": "sepal_length",
                        "y": "sepal_width",
                    },
                },
                {
                    "type": "graph",
                    "figure": {
                        "_target_": "__main__.custom_bar",
                        "data_frame": "iris",
                        "x": "sepal_length",
                        "y": "sepal_width",
                    },
                },
                {
                    "type": "graph",
                    "figure": {
                        "_target_": "custom_bar2",
                        "data_frame": "iris",
                    },
                },
                {"type": "ag_grid", "figure": {"_target_": "__main__.custom_grid", "data_frame": "iris"}},
                {"type": "ag_grid", "figure": {"_target_": "weird_grid", "data_frame": "iris"}},
            ],
        }
    ],
}


@capture("graph")
def custom_bar(data_frame: str, x: str, y: str):
    return go.Figure(data=[go.Bar(x=data_frame[x], y=data_frame[y])])


@capture("ag_grid")
def custom_grid(data_frame: pd.DataFrame) -> dag.AgGrid:
    """Custom Grid."""
    defaults = {
        "className": "ag-theme-quartz-dark ag-theme-vizro",
        "columnDefs": [{"field": col} for col in data_frame.columns],
        "rowData": data_frame.apply(
            lambda x: (
                x.dt.strftime("%Y-%m-%d")  # set date columns to `dateString` for AG Grid filtering to function
                if pd.api.types.is_datetime64_any_dtype(x)
                else x
            )
        ).to_dict("records"),
        "defaultColDef": {
            "resizable": True,
            "sortable": True,
            "filter": True,
            "flex": 1,
            "filterParams": {
                "buttons": ["apply", "reset"],
                "closeOnApply": True,
            },
        },
        "dashGridOptions": {
            "animateRows": False,
            "domLayout": "autoHeight",
            "pagination": True,
            "paginationPageSize": 20,
        },
    }
    return dag.AgGrid(**defaults)


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
        dashboard_config, context={"callable_defs": [("custom_bar2", "graph"), ("weird_grid", "ag_grid")]}
    )
    print(dashboard._to_python())
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

    # graph = {
    #     "type": "graph",
    #     "figure": {
    #         "_target_": "custom_bar",
    #         "data_frame": "iris",
    #         "x": "sepal_length",
    #         "y": "sepal_width",
    #     },
    # }

    # model = vm.Graph.model_validate(graph, context={"callable_defs": ["custom_bar"]})

    # print(model._to_python())
