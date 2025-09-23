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
                    title="Filter interaction to AgGrid below",
                    figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
                    actions=[
                        set_control(control="p1_filter_1", value="species"),
                        set_control(control="p1_filter_2", value="customdata[0]"),
                    ],
                ),
                vm.Container(
                    components=[
                        vm.AgGrid(id="p1_ag_grid_1", figure=dash_ag_grid(df)),
                    ],
                    controls=[
                        # multi=True
                        vm.Filter(id="p1_filter_1", column="species", targets=["p1_ag_grid_1"]),
                        # multi=False
                        vm.Filter(
                            id="p1_filter_2",
                            column="species",
                            targets=["p1_ag_grid_1"],
                            selector=vm.Dropdown(multi=False),
                        ),
                    ],
                ),
            ],
        ),
        vm.Container(
            title="Graph Drill-through to Page 2",
            variant="outlined",
            layout=vm.Grid(grid=[[0, 1]]),
            components=[
                vm.Graph(
                    title="Drill-through to multi=True Page-2",
                    figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
                    actions=set_control(control="p2_filter_1", value="species"),
                ),
                vm.Graph(
                    title="Drill-through to multi=False Page-2",
                    figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
                    actions=set_control(control="p2_filter_2", value="species"),
                ),
            ],
        ),
    ],
)

page_2 = vm.Page(
    title="Graph Drill-through target page",
    components=[
        vm.Graph(
            figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"),
        )
    ],
    controls=[
        # multi=True
        vm.Filter(id="p2_filter_1", column="species", show_in_url=True, selector=vm.Checklist()),
        # multi=False
        vm.Filter(id="p2_filter_2", column="species", show_in_url=True, selector=vm.RadioItems()),
    ],
)

# ====== Graph drill-down ======

vm.Page.add_type("controls", vm.Button)


@capture("graph")
def graph_with_dynamic_title(data_frame, title="ALL", **kwargs):
    return px.scatter(data_frame, title=f"Graph shows `{title}` species.", **kwargs)


page_3 = vm.Page(
    title="Graph Drill-down page",
    components=[
        vm.Graph(
            id="p3_graph_1",
            figure=graph_with_dynamic_title(
                data_frame=df, x="sepal_width", y="sepal_length", color="species", custom_data=["species"]
            ),
            actions=[
                set_control(control="p3-filter-1", value="species"),
                set_control(control="p3-parameter-1", value="species"),
            ],
        )
    ],
    controls=[
        # Hidden with the custom css
        vm.Filter(id="p3-filter-1", column="species"),
        vm.Parameter(
            id="p3-parameter-1",
            targets=["p3_graph_1.title"],
            selector=vm.Dropdown(options=["setosa", "versicolor", "virginica"]),
        ),
        vm.Button(
            text="Reset drill down",
            icon="Reset Focus",
            actions=[
                vm.Action(
                    function=capture("action")(
                        lambda: [["setosa", "versicolor", "virginica"], ["setosa", "versicolor", "virginica"]]
                    )(),
                    outputs=["p3-filter-1", "p3-parameter-1"],
                ),
                # Forget the button right now!!
                # set_control(control="p3-filter-1", value=["setosa", "versicolor", "virginica"])
                # set_control(control="p3-parameter-1", value=["setosa", "versicolor", "virginica"])
            ],
        ),
    ],
)


# ====== AG-GRID ======

page_4 = vm.Page(
    title="AgGrid filter interactions and drill-through source page",
    components=[
        vm.Container(
            title="Two filter interactions within Page 1",
            layout=vm.Grid(grid=[[0, 1]]),
            variant="outlined",
            components=[
                vm.AgGrid(
                    title="Filter interaction to Graph below",
                    figure=dash_ag_grid(df, dashGridOptions={"rowSelection": {"checkboxes": True}}),
                    actions=[
                        set_control(control="p4_filter_1", value="species"),
                        set_control(control="p4_filter_2", value="species"),
                        set_control(control="p4_filter_3", value="species"),
                        set_control(control="p4_filter_4", value="species"),
                    ],
                ),
                vm.Container(
                    components=[
                        vm.Graph(
                            id="p4_graph_1", figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species")
                        ),
                    ],
                    controls=[
                        # multi=True
                        vm.Filter(id="p4_filter_1", column="species", targets=["p4_graph_1"]),
                        # multi=False
                        vm.Filter(
                            id="p4_filter_2",
                            column="species",
                            targets=["p4_graph_1"],
                            selector=vm.Dropdown(multi=False),
                        ),
                        # multi=False
                        vm.Filter(id="p4_filter_3", column="species", targets=["p4_graph_1"], selector=vm.RadioItems()),
                        # multi=True
                        vm.Filter(id="p4_filter_4", column="species", targets=["p4_graph_1"], selector=vm.Checklist()),
                    ],
                ),
            ],
        ),
        vm.Container(
            title="AgGrid Drill-through to Page 5",
            variant="outlined",
            layout=vm.Grid(grid=[[0, 1]]),
            components=[
                vm.AgGrid(
                    figure=dash_ag_grid(df),
                    title="Drill-through to multi=True Page-5",
                    actions=set_control(control="p5_filter_1", value="species"),
                ),
                vm.AgGrid(
                    figure=dash_ag_grid(df),
                    title="Drill-through to multi=False Page-5",
                    actions=set_control(control="p5_filter_2", value="species"),
                ),
            ],
        ),
    ],
)

page_5 = vm.Page(
    title="AgGrid Drill-through target page",
    components=[vm.Graph(figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"))],
    controls=[
        # multi=True
        vm.Filter(id="p5_filter_1", column="species", show_in_url=True, selector=vm.Checklist()),
        # multi=False
        vm.Filter(id="p5_filter_2", column="species", show_in_url=True, selector=vm.RadioItems()),
    ],
)


dashboard = vm.Dashboard(
    pages=[page_1, page_2, page_3, page_4, page_5],
    navigation=vm.Navigation(
        pages={
            "Graph as source": [
                "Graph filter interactions and drill-through source page",
                "Graph Drill-through target page",
                "Graph Drill-down page",
            ],
            "AgGrid as source": [
                "AgGrid filter interactions and drill-through source page",
                "AgGrid Drill-through target page",
            ],
        }
    ),
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
