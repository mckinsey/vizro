"""This is a test app to test the dashboard layout."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture
from vizro.actions import set_control
from vizro.tables import dash_ag_grid

df = px.data.iris()


page_1 = vm.Page(
    title="Graph filter interactions and drill-through source page",
    components=[
        vm.Container(
            title="Two filter interactions within Page 1",
            layout=vm.Grid(grid=[[0, 1]]),
            variant="outlined",
            components=[
                vm.Graph(
                    id="p1_graph_1",
                    title="Filter interaction to AgGrid below",
                    figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
                    actions=[
                        set_control(target="p1_filter_1"),
                        set_control(target="p1_filter_2"),
                    ]
                ),
                vm.Container(
                    components=[
                        vm.AgGrid(
                            id="p1_ag_grid_1",
                            figure=dash_ag_grid(df, id="p1_inner_ag_grid_1")
                        ),
                    ],
                    controls=[
                        # multi=True
                        vm.Filter(id="p1_filter_1", column="species", targets=["p1_ag_grid_1"]),
                        # multi=False
                        vm.Filter(id="p1_filter_2", column="species", targets=["p1_ag_grid_1"], selector=vm.Dropdown(multi=False))
                    ]
                )

            ]
        ),
        vm.Container(
            title="Drill-through to Page 2",
            variant="outlined",
            layout=vm.Grid(grid=[[0, 1]]),
            components=[
                vm.Graph(
                    id="p1_graph_2",
                    title="Drill-through to multi=True Page-2",
                    figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
                    actions=set_control(target="p2_filter_1")
                ),
                vm.Graph(
                    id="p1_graph_3",
                    title="Drill-through to multi=False Page-2",
                    figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
                    actions=set_control(target="p2_filter_2")
                ),
            ]
        )
    ],
)

page_2 = vm.Page(
    title="Drill-through target page",
    components=[
        vm.Graph(
            id="p2_graph_1",
            figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"),
        )
    ],
    controls=[
        # multi=True
        vm.Filter(id="p2_filter_1", column="species", show_in_url=True, selector=vm.Checklist()),
        # multi=False
        vm.Filter(id="p2_filter_2", column="species", show_in_url=True, selector=vm.RadioItems()),
    ]
)


vm.Page.add_type("controls", vm.Button)


@capture("graph")
def graph_with_dynamic_title(data_frame, title="ALL", **kwargs):
    return px.scatter(data_frame, title=f"Graph shows `{title}` species.", **kwargs)


page_3 = vm.Page(
    title="Drill-down page",
    components=[
        vm.Graph(
            id="p3_graph_1",
            figure=graph_with_dynamic_title(data_frame=df, x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
            actions=[set_control(target="p3_filter_1"), set_control(target="p3_parameter_1")]
        )
    ],
    controls=[
        # Hidden with the custom css
        vm.Filter(id="p3_filter_1", column="species"),
        vm.Parameter(
            id="p3_parameter_1",
            targets=["p3_graph_1.title"],
            selector=vm.Dropdown(options=["setosa", "versicolor", "virginica"])
        ),
        vm.Button(
            text="Reset drill down", icon="Reset Focus",
            actions=vm.Action(
                function=capture("action")(lambda: [["setosa", "versicolor", "virginica"], ["setosa", "versicolor", "virginica"]])(),
                outputs=["p3_filter_1", "p3_parameter_1"]
           )
        )
    ]
)

dashboard = vm.Dashboard(pages=[page_1, page_2, page_3])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
