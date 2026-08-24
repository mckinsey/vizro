"""This is a test app to test the dashboard layout."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager
from vizro.actions import set_control, update_targets


df = px.data.iris()
data_manager["dynamic_iris"] = lambda number_of_points=10: df.head(number_of_points)


SPECIES_COLORS = {"setosa": "#00b4ff", "versicolor": "#ff9222", "virginica": "#3949ab"}

vm.Page.add_type("controls", vm.Button)


page_0_1 = vm.Page(
    id="page_0_1",
    title="Smoke test Page",
    components=[
        vm.Graph(
            id="p01_graph",
            figure=px.scatter(
                "dynamic_iris", x="sepal_width", y="sepal_length", color="species", color_discrete_map=SPECIES_COLORS
            ),
        ),
        vm.Text(id="p01_text", text="Placeholder"),
    ],
    controls=[
        vm.Filter(id="p01_filter", column="species", selector=vm.RadioItems(), show_in_url=True),
        vm.Parameter(
            id="p01_parameter",
            targets=["p01_graph.data_frame.number_of_points"],
            selector=vm.Slider(min=10, max=150, step=10, value=10),
            show_in_url=True,
        ),
    ],
)

# ====== **FIX** vm.Filter/vm.Parameter always applied when targets refresh ======

page_1_1 = vm.Page(
    id="page_1_1",
    title="Apply the filter on the parameter change",
    components=[
        vm.Graph(
            id="p11_graph",
            figure=px.scatter(
                df, x="sepal_width", y="sepal_length", color="species", color_discrete_map=SPECIES_COLORS
            ),
        ),
    ],
    controls=[
        vm.Filter(
            column="species",
            targets=["p11_graph"],
            selector=vm.RadioItems(
                title="Filter that does NOT auto-apply, but is taken into account when its target Graph is updated.",
                # actions=None (or actions=[]) opts out of the default "refresh on change" behavior.
                actions=None,
            ),
        ),
        vm.Parameter(targets=["p11_graph.x"], selector=vm.RadioItems(options=["sepal_width", "sepal_length"])),
    ],
)


# ====== **NEW** Apply controls on button click ======


page_2_1 = vm.Page(
    id="page_2_1",
    title="Apply controls on button click",
    components=[
        vm.Graph(
            id="p21_graph",
            figure=px.scatter(
                df, x="sepal_width", y="sepal_length", color="species", color_discrete_map=SPECIES_COLORS
            ),
        ),
    ],
    controls=[
        vm.Filter(
            column="species",
            targets=["p21_graph"],
            selector=vm.RadioItems(
                title="Filter that does NOT auto-apply, but is taken into account when its target Graph is updated.",
                actions=None,
            ),
        ),
        vm.Parameter(
            targets=["p21_graph.x"],
            selector=vm.RadioItems(
                title="Parameter that does NOT auto-apply, but is taken into account when its target Graph is updated.",
                options=["sepal_width", "sepal_length"],
                actions=[],
            ),
        ),
        vm.Button(text="Apply controls", actions=update_targets()),
    ],
)

# ====== **NEW** A Slider resizes the data and refreshes two filters; Button then applies them ======
# The Slider is a data_frame Parameter, so its value resizes the graph's data. Its `update_targets` refreshes the two
# dynamic filters below on value change - recomputing the RadioItems options and the Slider min/max from the resized
# data - WITHOUT redrawing the graph (only the filters are targeted). The filters do NOT auto-apply; the Button
# applies them to the graph on click. The slider->filters step targets only filters (no figure), exercising the fix.

page_2_2 = vm.Page(
    id="page_2_2",
    title="Refresh filters with a slider, apply them with a button",
    components=[
        vm.Graph(
            id="p22_graph",
            figure=px.scatter(
                "dynamic_iris", x="sepal_width", y="sepal_length", color="species", color_discrete_map=SPECIES_COLORS
            ),
        ),
    ],
    controls=[
        vm.Parameter(
            id="p22_master_slider",
            targets=["p22_graph.data_frame.number_of_points"],
            selector=vm.Slider(
                min=10,
                max=150,
                step=10,
                value=10,
                title="Change me to resize the data and refresh the two filters below (graph is not redrawn).",
                actions=update_targets(targets=["p22_radio_filter", "p22_range_filter"]),
            ),
        ),
        vm.Filter(
            id="p22_radio_filter",
            column="species",
            targets=["p22_graph"],
            selector=vm.RadioItems(
                title="Options refreshed by the slider; does NOT auto-apply.",
                actions=None,
            ),
        ),
        vm.Filter(
            id="p22_range_filter",
            column="petal_length",
            targets=["p22_graph"],
            selector=vm.RangeSlider(
                title="min/max refreshed by the slider; does NOT auto-apply.",
                actions=[],
            ),
        ),
        vm.Button(text="Apply filters", actions=update_targets(targets=["p22_graph"])),
    ],
)

# ====== **NEW** A deferred data_frame Parameter is still applied when its targets are refreshed ======
# The Parameter (Slider) resizes the graph's data but has `actions=None`, so changing it does nothing on its own. The
# Filter is likewise deferred (`actions=[]`). Clicking the Button refreshes the whole page (bare `update_targets()`):
# the graph reloads with the new data size AND the filter's options recompute to match - proving the deferred
# parameter's value is counted even though it never triggered a refresh itself.

page_2_3 = vm.Page(
    id="page_2_3",
    title="Deferred parameter is still applied on refresh",
    components=[
        vm.Graph(
            id="p23_graph",
            figure=px.scatter(
                "dynamic_iris", x="sepal_width", y="sepal_length", color="species", color_discrete_map=SPECIES_COLORS
            ),
        ),
    ],
    controls=[
        vm.Parameter(
            id="p23_parameter",
            targets=["p23_graph.data_frame.number_of_points"],
            selector=vm.Slider(
                min=10,
                max=150,
                step=10,
                value=10,
                title="Resizes the data but does NOT auto-apply; its value is honored on the next refresh.",
                actions=None,
            ),
        ),
        vm.Filter(
            id="p23_filter",
            column="species",
            targets=["p23_graph"],
            selector=vm.RadioItems(
                title="Dynamic filter; options recompute from the resized data on refresh.",
                actions=[],
            ),
        ),
        vm.Button(text="Refresh Filter", actions=update_targets(targets=["p23_filter"])),
        vm.Button(text="Refresh Graph", actions=update_targets(targets=["p23_graph"])),
        vm.Button(text="Refresh everything on the page", actions=update_targets()),
    ],
)


# ====== **NEW** Synced control values (chained actions) ======

page_3_1 = vm.Page(
    id="page_3_1",
    title="Sync: By chaining builtin actions",
    layout=vm.Grid(grid=[[0, 1]]),
    components=[
        vm.Container(
            controls=[
                vm.Filter(
                    id="p31_filter_1",
                    column="species",
                    selector=vm.Dropdown(
                        actions=[
                            update_targets(targets=["p31_graph_1"]),
                            set_control(control="p31_filter_2", value=None),
                        ]
                    ),
                )
            ],
            components=[
                vm.Graph(id="p31_graph_1", figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"))
            ],
        ),
        vm.Container(
            controls=[
                vm.Filter(
                    id="p31_filter_2",
                    column="species",
                    selector=vm.Checklist(
                        actions=[
                            update_targets(targets=["p31_graph_2"]),
                            set_control(control="p31_filter_1", value=None),
                        ]
                    ),
                ),
            ],
            components=[
                vm.Graph(id="p31_graph_2", figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"))
            ],
        ),
    ],
)


page_3_2 = vm.Page(
    id="page_3_2",
    title="Sync: By targeting a filter",
    layout=vm.Grid(grid=[[0, 1]]),
    components=[
        vm.Container(
            controls=[vm.Filter(id="p22_filter_1", column="species", targets=["p22_graph_1", "p22_filter_2"])],
            components=[
                vm.Graph(id="p22_graph_1", figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"))
            ],
        ),
        vm.Container(
            controls=[
                vm.Filter(
                    id="p22_filter_2",
                    column="species",
                    targets=["p22_graph_2", "p22_filter_1"],
                    selector=vm.Checklist(),
                ),
            ],
            components=[
                vm.Graph(id="p22_graph_2", figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"))
            ],
        ),
    ],
)

page_3_3 = vm.Page(
    id="page_3_3",
    title="Sync: By targeting a hidden parameter",
    components=[
        vm.Graph(
            id="p23_graph_1",
            figure=px.scatter(
                df, x="sepal_width", y="sepal_length", color="species", color_discrete_map=SPECIES_COLORS
            ),
        )
    ],
    controls=[
        vm.Filter(column="species", targets=["p23_graph_1", "p23_parameter_1"], selector=vm.RadioItems()),
        vm.Parameter(
            id="p23_parameter_1",
            targets=["p23_graph_1.title"],
            selector=vm.RadioItems(options=["setosa", "versicolor", "virginica"], value="setosa"),
            visible=False,
        ),
    ],
)


# TODO-REVIEWER: 8https
page_3_4 = vm.Page(
    id="page_3_4",
    title="Sync: Filter targets a filter that targets a filter x4",
    layout=vm.Grid(grid=[[0, 1], [2, 3]]),
    components=[
        vm.Container(
            controls=[vm.Filter(id="p24_filter_1", column="species", targets=["p24_graph_1", "p24_filter_2"])],
            components=[
                vm.Graph(id="p24_graph_1", figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"))
            ],
        ),
        vm.Container(
            controls=[
                vm.Filter(
                    id="p24_filter_2",
                    column="species",
                    targets=["p24_graph_2", "p24_filter_3"],
                    selector=vm.Checklist(),
                ),
            ],
            components=[
                vm.Graph(id="p24_graph_2", figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"))
            ],
        ),
        vm.Container(
            controls=[
                vm.Filter(
                    id="p24_filter_3",
                    column="species",
                    targets=["p24_graph_3", "p24_filter_4"],
                    selector=vm.Checklist(),
                ),
            ],
            components=[
                vm.Graph(id="p24_graph_3", figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"))
            ],
        ),
        vm.Container(
            controls=[
                vm.Filter(
                    id="p24_filter_4",
                    column="species",
                    targets=["p24_graph_4", "p24_filter_1"],
                    selector=vm.Checklist(),
                ),
            ],
            components=[
                vm.Graph(id="p24_graph_4", figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"))
            ],
        ),
    ],
)


# TODO-REVIEWER: 16+https
page_3_5 = vm.Page(
    id="page_3_5",
    title="Sync: Filter targets all filters x4",
    layout=vm.Grid(grid=[[0, 1], [2, 3]]),
    components=[
        vm.Container(
            controls=[
                vm.Filter(
                    id="p25_filter_1",
                    column="species",
                    targets=["p25_graph_1", "p25_filter_2", "p25_filter_3", "p25_filter_4"],
                )
            ],
            components=[
                vm.Graph(id="p25_graph_1", figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"))
            ],
        ),
        vm.Container(
            controls=[
                vm.Filter(
                    id="p25_filter_2",
                    column="species",
                    targets=["p25_graph_2", "p25_filter_1", "p25_filter_3", "p25_filter_4"],
                    selector=vm.Checklist(),
                ),
            ],
            components=[
                vm.Graph(id="p25_graph_2", figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"))
            ],
        ),
        vm.Container(
            controls=[
                vm.Filter(
                    id="p25_filter_3",
                    column="species",
                    targets=["p25_graph_3", "p25_filter_1", "p25_filter_2", "p25_filter_4"],
                    selector=vm.Checklist(),
                ),
            ],
            components=[
                vm.Graph(id="p25_graph_3", figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"))
            ],
        ),
        vm.Container(
            controls=[
                vm.Filter(
                    id="p25_filter_4",
                    column="species",
                    targets=["p25_graph_4", "p25_filter_1", "p25_filter_2", "p25_filter_3"],
                    selector=vm.Checklist(),
                ),
            ],
            components=[
                vm.Graph(id="p25_graph_4", figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"))
            ],
        ),
    ],
)


page_3_6 = vm.Page(
    id="page_3_6",
    title="Sync: Parameter targets Filter and Parameter",
    components=[
        vm.Graph(
            id="p26_graph_1",
            figure=px.scatter(
                df, x="sepal_width", y="sepal_length", color="species", color_discrete_map=SPECIES_COLORS
            ),
        )
    ],
    controls=[
        vm.Filter(
            id="p26_filter_1",
            column="species",
            targets=["p26_graph_1", "p26_parameter_1"],
            selector=vm.RadioItems(title="Filter that targets parameter below"),
        ),
        vm.Parameter(
            id="p26_parameter_1",
            targets=["p26_graph_1.title", "p26_filter_1"],
            selector=vm.RadioItems(
                title="Parameter that targets filter above", options=["setosa", "versicolor", "virginica"]
            ),
        ),
        vm.Parameter(
            id="p26_parameter_2",
            targets=["p26_graph_1.x", "p26_parameter_3"],
            selector=vm.RadioItems(
                title="Parameter that targets parameter below",
                options=["sepal_length", "petal_length"],
            ),
        ),
        vm.Parameter(
            id="p26_parameter_3",
            targets=["p26_graph_1.y", "p26_parameter_2"],
            selector=vm.RadioItems(
                title="Parameter that targets parameter above",
                options=["sepal_length", "petal_length"],
            ),
        ),
    ],
)


dashboard = vm.Dashboard(
    pages=[
        page_0_1,
        page_1_1,
        page_2_1,
        page_2_2,
        page_2_3,
        page_3_1,
        page_3_2,
        page_3_3,
        page_3_4,
        page_3_5,
        page_3_6,
    ],
    navigation=vm.Navigation(
        pages={
            "Playgrounds": ["page_0_1"],
            "Apply filter on parameter change": ["page_1_1"],
            "Apply controls on button click": ["page_2_1", "page_2_2", "page_2_3"],
            "Syncing controls": [
                "page_3_1",
                "page_3_2",
                "page_3_3",
                "page_3_4",
                "page_3_5",
                "page_3_6",
            ],
        }
    ),
)


if __name__ == "__main__":
    Vizro().build(dashboard).run()
