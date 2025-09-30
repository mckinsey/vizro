"""Dev app to try things out."""

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager


data_manager["dynamic_df"] = lambda: px.data.iris()

page_show_controls = vm.Page(
    title="Controls shown",
    components=[
        vm.Container(
            components=[
                vm.Graph(
                    id="graph_1", figure=px.scatter("dynamic_df", x="sepal_width", y="sepal_length", color="species")
                )
            ],
            controls=[
                vm.Filter(
                    column="species",
                    selector=vm.Checklist(title="Static Filter", options=["setosa", "virginica", "versicolor"]),
                ),
                vm.Filter(column="species", selector=vm.Checklist(title="Dynamic Filter")),
                vm.Parameter(
                    targets=["graph_1.x"],
                    selector=vm.RadioItems(
                        title="x-axis Parameter",
                        options=["sepal_width", "sepal_length", "petal_width", "petal_length"],
                        value="sepal_width",
                    ),
                ),
            ],
        )
    ],
    controls=[
        vm.Filter(
            column="species",
            selector=vm.Checklist(title="Static Filter", options=["setosa", "virginica", "versicolor"]),
        ),
        vm.Filter(column="species", selector=vm.Checklist(title="Dynamic Filter")),
        vm.Parameter(
            targets=["graph_1.y"],
            selector=vm.RadioItems(
                title="y-axis Parameter",
                options=["sepal_width", "sepal_length", "petal_width", "petal_length"],
                value="sepal_length",
            ),
        ),
    ],
)

page_no_controls = vm.Page(
    title="No controls",
    components=[
        vm.Container(
            components=[
                vm.Graph(
                    id="graph_2", figure=px.scatter("dynamic_df", x="sepal_width", y="sepal_length", color="species")
                )
            ],
        )
    ],
)

page_hidden_controls = vm.Page(
    title="Controls hidden",
    components=[
        vm.Container(
            components=[
                vm.Graph(
                    id="graph_3", figure=px.scatter("dynamic_df", x="sepal_width", y="sepal_length", color="species")
                )
            ],
            controls=[
                vm.Filter(
                    column="species",
                    selector=vm.Checklist(title="Static Filter", options=["setosa", "virginica", "versicolor"]),
                    hidden=True,
                ),
                vm.Filter(
                    column="species",
                    selector=vm.Checklist(title="Dynamic Filter"),
                    hidden=True,
                ),
                vm.Parameter(
                    targets=["graph_3.x"],
                    selector=vm.RadioItems(
                        title="x-axis Parameter",
                        options=["sepal_width", "sepal_length", "petal_width", "petal_length"],
                        value="sepal_width",
                    ),
                    hidden=True,
                ),
            ],
        )
    ],
    controls=[
        vm.Filter(
            column="species",
            selector=vm.Checklist(title="Static Filter", options=["setosa", "virginica", "versicolor"]),
            hidden=True,
        ),
        vm.Filter(
            column="species",
            selector=vm.Checklist(title="Dynamic Filter"),
            hidden=True,
        ),
        vm.Parameter(
            targets=["graph_3.y"],
            selector=vm.RadioItems(
                title="y-axis Parameter",
                options=["sepal_width", "sepal_length", "petal_width", "petal_length"],
                value="sepal_length",
            ),
            hidden=True,
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page_show_controls, page_no_controls, page_hidden_controls])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
