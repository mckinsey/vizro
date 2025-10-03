"""Dev app to try things out."""

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager

# TODO PP:
#  [DONE] Make PoC
#    [DONE] Make button
#    [DONE] Make vizro_controls_store
#    [DONE] Make js fun
#  [DONE] Make guardian existing for all filter/parameters
#  [DONE] Fix output OPL-trigger duplicate output issue.
#  [] scratch-app add all selectors to all pages. [static, dynamic, url, hidden]
#  [] Fix null originalValue added for p1_control_1_selector and maybe others
#  [] Fix comments
#  [] Investigate should the just adjust the sync_url except adding a new clientside callback.
#    [] Fix it exists only if there are controls on the page.


data_manager["dynamic_df"] = lambda: px.data.iris()

page_show_controls = vm.Page(
    id="page_1",
    title="All selectors page",
    components=[
        vm.Container(
            components=[
                vm.Graph(
                    id="graph_1", figure=px.scatter("dynamic_df", x="sepal_width", y="sepal_length", color="species")
                )
            ],
            controls=[
                # vm.Filter(
                #     id="p1_control_1",
                #     column="species",
                #     selector=vm.Checklist(
                #         id="p1_filter_1_selector",
                #         title="Static Filter",
                #         options=["setosa", "virginica", "versicolor"]
                #     ),
                # ),
                vm.Filter(
                    id="p1_control_2",
                    column="species", selector=vm.Checklist(
                        id="p1_filter_2_selector",
                        title="Dynamic Filter"
                    )
                ),
                vm.Parameter(
                    id="p1_control_3",
                    targets=["graph_1.x"],
                    selector=vm.RadioItems(
                        id="p1_parameter_3_selector",
                        title="x-axis Parameter",
                        options=["sepal_width", "sepal_length", "petal_width", "petal_length"],
                        value="sepal_width",
                    ),
                ),
            ],
        )
    ],
    controls=[
        # vm.Filter(
        #     id="p1_control_4",
        #     column="species",
        #     selector=vm.Checklist(
        #         id="p1_control_4_selector",
        #         title="Static Filter",
        #         options=["setosa", "virginica", "versicolor"]
        #     ),
        # ),
        vm.Filter(
            id="p1_control_5",
            column="species",
            selector=vm.Checklist(
                id="p1_control_5_selector",
                title="Dynamic Filter"
            )
        ),
        vm.Parameter(
            id="p1_control_6",
            targets=["graph_1.y"],
            selector=vm.RadioItems(
                id="p1_control_6_selector",
                title="y-axis Parameter",
                options=["sepal_width", "sepal_length", "petal_width", "petal_length"],
                value="sepal_length",
            ),
        ),
    ],
)

page_no_controls = vm.Page(
    id="page_2",
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
    id="page_3",
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
                    id="p3_control_1",
                    column="species",
                    selector=vm.Checklist(
                        id="p3_filter_1_selector",
                        title="Static Filter",
                        options=["setosa", "virginica", "versicolor"]
                    ),
                    visible=False,
                ),
                vm.Filter(
                    id="p3_control_2",
                    column="species",
                    selector=vm.Checklist(
                        id="p3_filter_2_selector",
                        title="Dynamic Filter"
                    ),
                    visible=False,
                ),
                vm.Parameter(
                    id="p3_control_3",
                    targets=["graph_3.x"],
                    selector=vm.RadioItems(
                        id="p3_parameter_3_selector",
                        title="x-axis Parameter",
                        options=["sepal_width", "sepal_length", "petal_width", "petal_length"],
                        value="sepal_width",
                    ),
                    visible=False,
                ),
            ],
        )
    ],
    controls=[
        vm.Filter(
            id="p3_control_4",
            column="species",
            selector=vm.Checklist(
                id="p3_control_4_selector",
                title="Static Filter",
                options=["setosa", "virginica", "versicolor"]
            ),
            visible=False,
        ),
        vm.Filter(
            id="p3_control_5",
            column="species",
            selector=vm.Checklist(
                id="p3_control_5_selector",
                title="Dynamic Filter"
            ),
            visible=False,
        ),
        vm.Parameter(
            id="p3_control_6",
            targets=["graph_3.y"],
            selector=vm.RadioItems(
                id="p3_control_6_selector",
                title="y-axis Parameter",
                options=["sepal_width", "sepal_length", "petal_width", "petal_length"],
                value="sepal_length",
            ),
            visible=False,
        ),
    ],
)

page_show_in_url = vm.Page(
    id="page_4",
    title="Controls hidden (updated IDs)",
    components=[
        vm.Container(
            components=[
                vm.Graph(
                    id="graph_4", figure=px.scatter("dynamic_df", x="sepal_width", y="sepal_length", color="species")
                )
            ],
            controls=[
                # vm.Filter(
                #     id="p4_control_1",
                #     column="species",
                #     selector=vm.Checklist(
                #         id="p4_filter_1_selector",
                #         title="Static Filter",
                #         options=["setosa", "virginica", "versicolor"]
                #     ),
                #     show_in_url=True,
                #     # visible=False,
                # ),
                vm.Filter(
                    id="p4_control_2",
                    column="species",
                    selector=vm.Checklist(
                        id="p4_filter_2_selector",
                        title="Dynamic Filter"
                    ),
                    show_in_url=True,
                    # visible=False,
                ),
                vm.Parameter(
                    id="p4_control_3",
                    targets=["graph_4.x"],
                    selector=vm.RadioItems(
                        id="p4_parameter_3_selector",
                        title="x-axis Parameter",
                        options=["sepal_width", "sepal_length", "petal_width", "petal_length"],
                        value="sepal_width",
                    ),
                    show_in_url=True,
                    # visible=False,
                ),
            ],
        )
    ],
    controls=[
        # vm.Filter(
        #     id="p4_control_4",
        #     column="species",
        #     selector=vm.Checklist(
        #         id="p4_control_4_selector",
        #         title="Static Filter",
        #         options=["setosa", "virginica", "versicolor"]
        #     ),
        #     show_in_url=True,
        #     # visible=False,
        # ),
        vm.Filter(
            id="p4_control_5",
            column="species",
            selector=vm.Checklist(
                id="p4_control_5_selector",
                title="Dynamic Filter"
            ),
            show_in_url=True,
            # visible=False,
        ),
        vm.Parameter(
            id="p4_control_6",
            targets=["graph_4.y"],
            selector=vm.RadioItems(
                id="p4_control_6_selector",
                title="y-axis Parameter",
                options=["sepal_width", "sepal_length", "petal_width", "petal_length"],
                value="sepal_length",
            ),
            show_in_url=True,
            # visible=False,
        ),
    ]
)

dashboard = vm.Dashboard(
    pages=[page_show_controls, page_no_controls, page_hidden_controls, page_show_in_url],
    navigation=vm.Navigation(nav_selector=vm.NavBar()),
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
