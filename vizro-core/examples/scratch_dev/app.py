"""This is a test app to test the dashboard layout."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import set_control, update_figures
from vizro.managers import data_manager
from vizro.models.types import capture


df = px.data.iris()
data_manager["dynamic_iris"] = lambda number_of_points=10: df.head(number_of_points)


SPECIES_COLORS = {"setosa": "#00b4ff", "versicolor": "#ff9222", "virginica": "#3949ab"}


# ====== Playground - Smoke test page ======

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


# ====== **FIX** vm.Filter vs _filter_action ======

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
        vm.Text(id="p11_text", text="Placeholder"),
    ],
    controls=[
        vm.Filter(
            column="species",
            targets=["p11_graph"],
            selector=vm.RadioItems(
                title="Filter that does NOT auto-apply, but is taken into account when its target Graph is updated.",
                actions=vm.Action(function=capture("action")(lambda _trigger: _trigger)(), outputs="p11_text"),
            ),
        ),
        vm.Parameter(targets=["p11_graph.x"], selector=vm.RadioItems(options=["sepal_width", "sepal_length"])),
    ],
)


# ====== **NEW** Apply controls on button click ======

vm.Page.add_type("controls", vm.Button)

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
        vm.Text(id="p21_text", text="Placeholder"),
    ],
    controls=[
        vm.Filter(
            column="species",
            targets=["p21_graph"],
            selector=vm.RadioItems(
                title="Filter that does NOT auto-apply, but is taken into account when its target Graph is updated.",
                actions=vm.Action(function=capture("action")(lambda _trigger: _trigger)(), outputs="p21_text"),
            ),
        ),
        vm.Parameter(
            targets=["p21_graph.x"],
            selector=vm.RadioItems(
                title="Parameter that does NOT auto-apply, but is taken into account when its target Graph is updated.",
                options=["sepal_width", "sepal_length"],
                actions=vm.Action(function=capture("action")(lambda _trigger: _trigger)(), outputs="p21_text"),
            ),
        ),
        vm.Button(text="Apply controls", actions=update_figures()),
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
                            update_figures(targets=["p31_graph_1"]),
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
                            update_figures(targets=["p31_graph_2"]),
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


# TODO AM-PP OQ: One set_control triggers another set_control - infinite loop? I think that nothing unexpected can
#  happen because the value is the same, but we need to verify that.
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


# TODO-REVIEWER: 14https
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


"""
# ====== Cascading controls ======
# TODO: Does not work as:
#  1. Form component does not support the `set_control` action yet.
#  2. Can't be used as and "value" and "options" have to be updated too.
#  3. TODO PP (CT): Can't be used with custom action/dash callback as "select_all" option will be overwritten. We should improve "select_all" here. Ben suggested the same.
#  4. Think about dynamic data here.
#  5. Think about persistence per cascading filter value. Investigate dash docs about this.

@capture("action")
def update_country_options_value(_trigger):
    continent = _trigger
    if continent:
        filtered_df = df_gapminder[df_gapminder["continent"].isin([continent])]
        options = [{"label": c, "value": c} for c in sorted(filtered_df["country"].unique())]
        value = [options[0]["value"]] if options else []
        return options, value
    return [], []
"""


# TODO OQs:
#  1. Should we enable that Filter targets a filter on another page?
#  2. Cascading control has an issue if target is multi dropdown as we need to add the __SELECT_ALL option.
#  3. Think about dynamic data here. If filter is targeted should we set it to _dynamic? Should update_figures be used
#   for cascading filters as update figures means recreating and set_control for syncing values? How about
#   if source and target filter have the same column -> use set_control (sync)
#   if columns are different, use _dynamic/recreating cascading filter (update_figures)?.
#   There's no dynamic parameters yet, so enable only syncing there, and not cascading.
#  4. Cascading control: Think about persistence per cascading filter value. Investigate dash docs about this.

dashboard = vm.Dashboard(
    pages=[
        page_0_1,
        page_1_1,
        page_2_1,
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
            "Apply controls on button click": ["page_2_1"],
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
