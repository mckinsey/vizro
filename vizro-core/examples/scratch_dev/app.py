"""This is a test app to test the dashboard layout."""

import datetime as dt

import pandas as pd

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager
from vizro.actions import set_control, update_targets


df = px.data.iris()
data_manager["dynamic_iris"] = lambda number_of_points=10: df.head(number_of_points)


# A synthetic dataset with a column of every type, so page_3_9 can exercise syncing for *every* selector.
_SYNC_N = 60
_SYNC_HIER = [("North", "New York"), ("North", "Boston"), ("South", "Miami"), ("South", "Austin")]


def _cyc(values):
    """Cycle ``values`` deterministically to length ``_SYNC_N`` (keeps the dataset reproducible)."""
    return [values[i % len(values)] for i in range(_SYNC_N)]


sync_df = pd.DataFrame(
    {
        "x": [i % 10 for i in range(_SYNC_N)],
        "y": [(i * 3) % 10 for i in range(_SYNC_N)],
        "cat_dropdown": _cyc(["A", "B", "C"]),  # categorical -> Dropdown
        "cat_checklist": _cyc(["X", "Y", "Z"]),  # categorical -> Checklist
        "cat_radio": _cyc(["P", "Q", "R"]),  # categorical -> RadioItems
        "num_slider": _cyc([0, 1, 2, 3, 4, 5]),  # numerical -> Slider
        "num_range": _cyc([0, 20, 40, 60, 80, 100]),  # numerical -> RangeSlider
        "date_col": pd.to_datetime(
            _cyc(["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"])
        ),  # date -> DatePicker
        "datetime_col": pd.to_datetime(  # datetime -> DateTimePicker
            _cyc(["2024-01-01 06:00", "2024-01-01 09:00", "2024-01-01 12:00", "2024-01-01 15:00"])
        ),
        "time_col": _cyc([dt.time(8, 0), dt.time(10, 30), dt.time(13, 0), dt.time(16, 30)]),  # time -> TimePicker
        "bool_col": _cyc([True, False]),  # boolean -> Switch
        "region": [_SYNC_HIER[i % 4][0] for i in range(_SYNC_N)],  # hierarchical parent -> Cascader
        "city": [_SYNC_HIER[i % 4][1] for i in range(_SYNC_N)],  # hierarchical leaf   -> Cascader
    }
)


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
            controls=[vm.Filter(id="p32_filter_1", column="species", targets=["p32_graph_1", "p32_filter_2"])],
            components=[
                vm.Graph(id="p32_graph_1", figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"))
            ],
        ),
        vm.Container(
            controls=[
                vm.Filter(
                    id="p32_filter_2",
                    column="species",
                    targets=["p32_graph_2", "p32_filter_1"],
                    selector=vm.Checklist(),
                ),
            ],
            components=[
                vm.Graph(id="p32_graph_2", figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"))
            ],
        ),
    ],
)

page_3_3 = vm.Page(
    id="page_3_3",
    title="Sync: By targeting a hidden parameter",
    components=[
        vm.Graph(
            id="p33_graph_1",
            figure=px.scatter(
                df, x="sepal_width", y="sepal_length", color="species", color_discrete_map=SPECIES_COLORS
            ),
        )
    ],
    controls=[
        vm.Filter(column="species", targets=["p33_graph_1", "p33_parameter_1"], selector=vm.RadioItems()),
        vm.Parameter(
            id="p33_parameter_1",
            targets=["p33_graph_1.title"],
            selector=vm.RadioItems(options=["setosa", "versicolor", "virginica"], value="setosa"),
            visible=False,
        ),
    ],
)


page_3_4 = vm.Page(
    id="page_3_4",
    title="Sync: Filter targets a filter that targets a filter x4",
    layout=vm.Grid(grid=[[0, 1], [2, 3]]),
    components=[
        vm.Container(
            controls=[vm.Filter(id="p34_filter_1", column="species", targets=["p34_graph_1", "p34_filter_2"])],
            components=[
                vm.Graph(id="p34_graph_1", figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"))
            ],
        ),
        vm.Container(
            controls=[
                vm.Filter(
                    id="p34_filter_2",
                    column="species",
                    targets=["p34_graph_2", "p34_filter_3"],
                    selector=vm.Checklist(),
                ),
            ],
            components=[
                vm.Graph(id="p34_graph_2", figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"))
            ],
        ),
        vm.Container(
            controls=[
                vm.Filter(
                    id="p34_filter_3",
                    column="species",
                    targets=["p34_graph_3", "p34_filter_4"],
                    selector=vm.Checklist(),
                ),
            ],
            components=[
                vm.Graph(id="p34_graph_3", figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"))
            ],
        ),
        vm.Container(
            controls=[
                vm.Filter(
                    id="p34_filter_4",
                    column="species",
                    targets=["p34_graph_4", "p34_filter_1"],
                    selector=vm.Checklist(),
                ),
            ],
            components=[
                vm.Graph(id="p34_graph_4", figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"))
            ],
        ),
    ],
)


page_3_5 = vm.Page(
    id="page_3_5",
    title="Sync: Filter targets all filters x4",
    layout=vm.Grid(grid=[[0, 1], [2, 3]]),
    components=[
        vm.Container(
            controls=[
                vm.Filter(
                    id="p35_filter_1",
                    column="species",
                    targets=["p35_graph_1", "p35_filter_2", "p35_filter_3", "p35_filter_4"],
                )
            ],
            components=[
                vm.Graph(id="p35_graph_1", figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"))
            ],
        ),
        vm.Container(
            controls=[
                vm.Filter(
                    id="p35_filter_2",
                    column="species",
                    targets=["p35_graph_2", "p35_filter_1", "p35_filter_3", "p35_filter_4"],
                    selector=vm.Checklist(),
                ),
            ],
            components=[
                vm.Graph(id="p35_graph_2", figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"))
            ],
        ),
        vm.Container(
            controls=[
                vm.Filter(
                    id="p35_filter_3",
                    column="species",
                    targets=["p35_graph_3", "p35_filter_1", "p35_filter_2", "p35_filter_4"],
                    selector=vm.Checklist(),
                ),
            ],
            components=[
                vm.Graph(id="p35_graph_3", figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"))
            ],
        ),
        vm.Container(
            controls=[
                vm.Filter(
                    id="p35_filter_4",
                    column="species",
                    targets=["p35_graph_4", "p35_filter_1", "p35_filter_2", "p35_filter_3"],
                    selector=vm.Checklist(),
                ),
            ],
            components=[
                vm.Graph(id="p35_graph_4", figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"))
            ],
        ),
    ],
)


page_3_6 = vm.Page(
    id="page_3_6",
    title="Sync: Parameter targets Filter and Parameter",
    components=[
        vm.Graph(
            id="p36_graph_1",
            figure=px.scatter(
                df, x="sepal_width", y="sepal_length", color="species", color_discrete_map=SPECIES_COLORS
            ),
        )
    ],
    controls=[
        vm.Filter(
            id="p36_filter_1",
            column="species",
            targets=["p36_graph_1", "p36_parameter_1"],
            selector=vm.RadioItems(title="Filter that targets parameter below"),
        ),
        vm.Parameter(
            id="p36_parameter_1",
            targets=["p36_graph_1.title", "p36_filter_1"],
            selector=vm.RadioItems(
                title="Parameter that targets filter above", options=["setosa", "versicolor", "virginica"]
            ),
        ),
        vm.Parameter(
            id="p36_parameter_2",
            targets=["p36_graph_1.x", "p36_parameter_3"],
            selector=vm.RadioItems(
                title="Parameter that targets parameter below",
                options=["sepal_length", "petal_length"],
            ),
        ),
        vm.Parameter(
            id="p36_parameter_3",
            targets=["p36_graph_1.y", "p36_parameter_2"],
            selector=vm.RadioItems(
                title="Parameter that targets parameter above",
                options=["sepal_length", "petal_length"],
            ),
        ),
    ],
)


# ====== **NEW** Synced controls, applied to the graph on button click ======
# Like page_3_6 (F<->P and P<->P sync) but with an extra F<->F pair, so all three sync kinds are present:
#   F<->F: p37_filter_1    <-> p37_filter_2
#   F<->P: p37_filter_3    <-> p37_parameter_1
#   P<->P: p37_parameter_2 <-> p37_parameter_3
# Each selector carries an explicit `set_control` action (and no auto `update_targets`), so changing a control syncs
# its partner but does NOT redraw the graph. When the selector has explicit actions the sync is wired manually via
# `set_control`, so the partner's id must NOT also be listed in `targets` (it would be stripped as dead config and
# warn). A Filter needs no figure target here - it falls back to the page graph - but a Parameter must have a figure
# target, so each parameter targets a `p37_graph_1` argument. The pairs stay in sync on change via `set_control`;
# the "Apply to graph" button runs `update_targets()` to refresh the graph with the current (synced) control values.
page_3_7 = vm.Page(
    id="page_3_7",
    title="Sync: Controls sync each other; graph applied on button click",
    components=[
        vm.Graph(
            id="p37_graph_1",
            figure=px.scatter(
                df, x="sepal_width", y="sepal_length", color="species", color_discrete_map=SPECIES_COLORS
            ),
        )
    ],
    controls=[
        # F <-> F
        vm.Filter(
            id="p37_filter_1",
            column="species",
            selector=vm.RadioItems(
                title="F1 <-> F2 (syncs filter below; graph applied on button click)",
                actions=[set_control(control="p37_filter_2", value=None)],
            ),
        ),
        vm.Filter(
            id="p37_filter_2",
            column="species",
            selector=vm.Checklist(
                title="F2 <-> F1 (syncs filter above; graph applied on button click)",
                actions=[set_control(control="p37_filter_1", value=None)],
            ),
        ),
        # F <-> P
        vm.Filter(
            id="p37_filter_3",
            column="species",
            selector=vm.RadioItems(
                title="F3 <-> P1 (syncs parameter below)",
                actions=[set_control(control="p37_parameter_1", value=None)],
            ),
        ),
        vm.Parameter(
            id="p37_parameter_1",
            targets=["p37_graph_1.title"],
            selector=vm.RadioItems(
                title="P1 <-> F3 (syncs filter above; graph title applied on button click)",
                options=["setosa", "versicolor", "virginica"],
                actions=[set_control(control="p37_filter_3", value=None)],
            ),
        ),
        # P <-> P
        vm.Parameter(
            id="p37_parameter_2",
            targets=["p37_graph_1.x"],
            selector=vm.RadioItems(
                title="P2 <-> P3 (syncs parameter below; graph x applied on button click)",
                options=["sepal_length", "petal_length"],
                actions=[set_control(control="p37_parameter_3", value=None)],
            ),
        ),
        vm.Parameter(
            id="p37_parameter_3",
            targets=["p37_graph_1.y"],
            selector=vm.RadioItems(
                title="P3 <-> P2 (syncs parameter above; graph y applied on button click)",
                options=["sepal_length", "petal_length"],
                actions=[set_control(control="p37_parameter_2", value=None)],
            ),
        ),
        vm.Button(text="Apply to graph", actions=update_targets()),
    ],
)


page_3_8 = vm.Page(
    id="page_3_8",
    title="[Example from the PR description] Sync: Filters cross-target two graphs and each other",
    # Schema (F-filter, G-graph):
    #   F1 --> F2, F1 --> G1
    #   F2 --> F1, F2 --> G2, F2 --> F3
    #   F3 --> G2
    # F1.targets=[F2, G1]; F2.targets=[F1, G2, F3]; F3.targets=[G2]
    layout=vm.Grid(grid=[[0, 1]]),
    components=[
        vm.Graph(
            id="p38_graph_1",
            figure=px.scatter(
                df, x="sepal_width", y="sepal_length", color="species", color_discrete_map=SPECIES_COLORS
            ),
        ),
        vm.Graph(
            id="p38_graph_2",
            figure=px.scatter(
                df, x="sepal_width", y="sepal_length", color="species", color_discrete_map=SPECIES_COLORS
            ),
        ),
    ],
    controls=[
        vm.Filter(
            id="p38_filter_1",
            column="species",
            targets=["p38_filter_2", "p38_graph_1"],
            selector=vm.RadioItems(title="F1 -> [F2, G1]"),
        ),
        vm.Filter(
            id="p38_filter_2",
            column="species",
            targets=["p38_filter_1", "p38_graph_2", "p38_filter_3"],
            selector=vm.Checklist(title="F2 -> [F1, G2, F3]"),
        ),
        vm.Filter(
            id="p38_filter_3",
            column="species",
            targets=["p38_graph_2"],
            selector=vm.Checklist(title="F3 -> [G2]"),
        ),
    ],
)


# ====== **NEW** Every selector type syncing (manual test bench) ======
# One pair of filters per selector type, each filter targeting its twin so the two stay in sync. Filters need no
# figure target here - a control-only filter falls back to the page graph - so changing one selector both syncs its
# twin and refreshes the graph. This is the page to eyeball that syncing works for *every* selector, including the
# TimePicker / DateTimePicker / Cascader that only recently gained `_get_value_from_trigger`.
page_3_9 = vm.Page(
    id="page_3_9",
    title="Sync: Every selector type (manual test bench)",
    components=[vm.Graph(id="p39_graph_1", figure=px.scatter(sync_df, x="x", y="y"))],
    controls=[
        # Dropdown <-> Dropdown
        vm.Filter(
            id="p39_dropdown_1",
            column="cat_dropdown",
            targets=["p39_dropdown_2"],
            selector=vm.Dropdown(title="Dropdown 1 (syncs Dropdown 2)"),
        ),
        vm.Filter(
            id="p39_dropdown_2",
            column="cat_dropdown",
            targets=["p39_dropdown_1"],
            selector=vm.Dropdown(title="Dropdown 2 (syncs Dropdown 1)"),
        ),
        # Checklist <-> Checklist
        vm.Filter(
            id="p39_checklist_1",
            column="cat_checklist",
            targets=["p39_checklist_2"],
            selector=vm.Checklist(title="Checklist 1 (syncs Checklist 2)"),
        ),
        vm.Filter(
            id="p39_checklist_2",
            column="cat_checklist",
            targets=["p39_checklist_1"],
            selector=vm.Checklist(title="Checklist 2 (syncs Checklist 1)"),
        ),
        # RadioItems <-> RadioItems
        vm.Filter(
            id="p39_radio_1",
            column="cat_radio",
            targets=["p39_radio_2"],
            selector=vm.RadioItems(title="RadioItems 1 (syncs RadioItems 2)"),
        ),
        vm.Filter(
            id="p39_radio_2",
            column="cat_radio",
            targets=["p39_radio_1"],
            selector=vm.RadioItems(title="RadioItems 2 (syncs RadioItems 1)"),
        ),
        # Slider <-> Slider
        vm.Filter(
            id="p39_slider_1",
            column="num_slider",
            targets=["p39_slider_2"],
            selector=vm.Slider(title="Slider 1 (syncs Slider 2)"),
        ),
        vm.Filter(
            id="p39_slider_2",
            column="num_slider",
            targets=["p39_slider_1"],
            selector=vm.Slider(title="Slider 2 (syncs Slider 1)"),
        ),
        # RangeSlider <-> RangeSlider
        vm.Filter(
            id="p39_range_1",
            column="num_range",
            targets=["p39_range_2"],
            selector=vm.RangeSlider(title="RangeSlider 1 (syncs RangeSlider 2)"),
        ),
        vm.Filter(
            id="p39_range_2",
            column="num_range",
            targets=["p39_range_1"],
            selector=vm.RangeSlider(title="RangeSlider 2 (syncs RangeSlider 1)"),
        ),
        # DatePicker <-> DatePicker
        vm.Filter(
            id="p39_date_1",
            column="date_col",
            targets=["p39_date_2"],
            selector=vm.DatePicker(title="DatePicker 1 (syncs DatePicker 2)"),
        ),
        vm.Filter(
            id="p39_date_2",
            column="date_col",
            targets=["p39_date_1"],
            selector=vm.DatePicker(title="DatePicker 2 (syncs DatePicker 1)"),
        ),
        # DateTimePicker <-> DateTimePicker
        vm.Filter(
            id="p39_datetime_1",
            column="datetime_col",
            targets=["p39_datetime_2"],
            selector=vm.DateTimePicker(title="DateTimePicker 1 (syncs DateTimePicker 2)"),
        ),
        vm.Filter(
            id="p39_datetime_2",
            column="datetime_col",
            targets=["p39_datetime_1"],
            selector=vm.DateTimePicker(title="DateTimePicker 2 (syncs DateTimePicker 1)"),
        ),
        # TimePicker <-> TimePicker
        vm.Filter(
            id="p39_time_1",
            column="time_col",
            targets=["p39_time_2"],
            selector=vm.TimePicker(title="TimePicker 1 (syncs TimePicker 2)"),
        ),
        vm.Filter(
            id="p39_time_2",
            column="time_col",
            targets=["p39_time_1"],
            selector=vm.TimePicker(title="TimePicker 2 (syncs TimePicker 1)"),
        ),
        # Switch <-> Switch
        vm.Filter(
            id="p39_switch_1",
            column="bool_col",
            targets=["p39_switch_2"],
            selector=vm.Switch(title="Switch 1 (syncs Switch 2)"),
        ),
        vm.Filter(
            id="p39_switch_2",
            column="bool_col",
            targets=["p39_switch_1"],
            selector=vm.Switch(title="Switch 2 (syncs Switch 1)"),
        ),
        # Cascader <-> Cascader (hierarchical: column is an ordered list of columns)
        vm.Filter(
            id="p39_cascader_1",
            column=["region", "city"],
            targets=["p39_cascader_2"],
            selector=vm.Cascader(title="Cascader 1 (syncs Cascader 2)"),
        ),
        vm.Filter(
            id="p39_cascader_2",
            column=["region", "city"],
            targets=["p39_cascader_1"],
            selector=vm.Cascader(title="Cascader 2 (syncs Cascader 1)"),
        ),
    ],
)


# ====== **NEW** Pure selectors (no Filter/Parameter) drive filters across tabs via explicit set_control ======
# A Filter/Parameter that targets no figure "is not a Filter/Parameter". So instead of a control-only Filter, a
# dashboard creator can drop a *bare selector* (RadioItems, RangeSlider, ...) straight into the layout and attach an
# explicit `set_control` to it: the selector then acts purely as a driver - on change it pushes its value to the
# target controls, which do the actual figure filtering. Bare selectors are normally only allowed inside a
# Filter/Parameter, so they must be whitelisted as components via the `add_type` hack.
#
# Layout: tab 1 = pure driver selectors (no figure); tabs 2 & 3 = the real Filters (one per selector type), each
# filtering that tab's own graph. Each tab-1 selector `set_control`s the matching Filter on BOTH tab 2 and tab 3.
_p310_specs = [
    ("radio", "cat_radio", vm.RadioItems, {"options": ["P", "Q", "R"], "value": "P"}),
    ("dropdown", "cat_dropdown", vm.Dropdown, {"options": ["A", "B", "C"], "value": ["A"]}),
    ("checklist", "cat_checklist", vm.Checklist, {"options": ["X", "Y", "Z"], "value": ["X"]}),
    ("slider", "num_slider", vm.Slider, {"min": 0, "max": 5, "step": 1, "value": 2}),
    ("range", "num_range", vm.RangeSlider, {"min": 0, "max": 100, "value": [20, 80]}),
    (
        "date",
        "date_col",
        vm.DatePicker,
        {"min": "2024-01-01", "max": "2024-01-04", "value": ["2024-01-02", "2024-01-03"]},
    ),
    (
        "datetime",
        "datetime_col",
        vm.DateTimePicker,
        {"min": "2024-01-01", "max": "2024-01-01", "value": ["2024-01-01", "2024-01-01"]},
    ),
    ("time", "time_col", vm.TimePicker, {"value": ["08:00", "16:30"]}),
    ("switch", "bool_col", vm.Switch, {"value": True}),
    (
        "cascader",
        ["region", "city"],
        vm.Cascader,
        {
            "options": {"North": ["New York", "Boston"], "South": ["Miami", "Austin"]},
            "multi": False,
            "value": "New York",
        },
    ),
]

# Whitelist each bare selector type as an allowed Container component (they are normally only allowed as selectors).
for _sel_type in {spec[2] for spec in _p310_specs}:
    vm.Container.add_type("components", _sel_type)

_p310_tab1, _p310_tab2, _p310_tab3 = [], [], []
for _key, _column, _sel_type, _cfg in _p310_specs:
    _t2_id, _t3_id = f"p310_t2_{_key}", f"p310_t3_{_key}"
    _p310_tab1.append(
        _sel_type(
            id=f"p310_t1_{_key}",
            title=f"{_key}: pure selector -> sets {_t2_id} & {_t3_id}",
            actions=[set_control(control=_t2_id, value=None), set_control(control=_t3_id, value=None)],
            **_cfg,
        )
    )
    _p310_tab2.append(vm.Filter(id=_t2_id, column=_column, selector=_sel_type()))
    _p310_tab3.append(vm.Filter(id=_t3_id, column=_column, selector=_sel_type()))

page_3_10 = vm.Page(
    id="page_3_10",
    title="Sync: Pure selectors drive filters across tabs",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(title="Drivers (pure selectors, no Filter)", layout=vm.Flex(), components=_p310_tab1),
                vm.Container(
                    title="Target tab A",
                    components=[vm.Graph(id="p310_graph_a", figure=px.scatter(sync_df, x="x", y="y"))],
                    controls=_p310_tab2,
                ),
                vm.Container(
                    title="Target tab B",
                    components=[vm.Graph(id="p310_graph_b", figure=px.scatter(sync_df, x="x", y="y"))],
                    controls=_p310_tab3,
                ),
            ]
        )
    ],
)


# ====== **NEW** Syncing controls across pages ======
# A Filter/Parameter can now list a control on ANOTHER page in its `targets`. Changing it writes the new value into the
# internal `vizro_controls_store`; the synced control picks that value up when its own page is opened. There is no page
# navigation and no global URL - the values simply stay in sync across pages within the session.

page_40 = vm.Page(
    id="page_40",
    title="Cross-page sync (Page A)",
    components=[
        vm.Graph(id="p40_graph", figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species")),
    ],
    controls=[
        vm.Filter(
            id="p40_species",
            column="species",
            # Target a control on ANOTHER page (page_41) as well as this page's graph.
            targets=["p41_speciessss", "p40_graph"],
            selector=vm.Dropdown(title="Species (synced with Page B)"),
            # show_in_url is independent of cross-page syncing; here it also mirrors this control in the URL.
            show_in_url=True,
        ),
    ],
)

page_41 = vm.Page(
    id="page_41",
    title="Cross-page sync (Page B)",
    components=[
        vm.Graph(id="p41_graph", figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species")),
    ],
    controls=[
        vm.Filter(
            id="p41_speciessss",
            column="species",
            # Sync back to Page A's control (two-way) as well as this page's graph.
            targets=["p41_graph"],
            selector=vm.Checklist(title="Species (synced with Page A)"),
        ),
    ],
)


# ====== **NEW** Drill-through across pages (navigates over the URL) ======
# Clicking a point sets a control on ANOTHER page AND navigates there. Because the trigger is a figure (not a control
# selector), set_control performs a drill-through: the clicked value is written to the internal store and the page
# changes over the URL to the target page, where the value is applied on open.

page_42 = vm.Page(
    id="page_42",
    title="Drill-through (source)",
    components=[
        vm.Graph(
            id="p42_graph",
            title="Drill-through (source) - targets control with NO URL",
            # custom_data carries the species so set_control can read the clicked point's species.
            figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species", custom_data="species"),
            # Drill-through to a target restored from the store only (target has no show_in_url).
            actions=set_control(control="p43_species", value="species"),
        ),
        vm.Graph(
            id="p42_graph_url",
            title="Drill-through (source) - targets control with URL",
            figure=px.scatter(df, x="petal_width", y="petal_length", color="species", custom_data="species"),
            # Drill-through to a target that ALSO persists in the URL (target has show_in_url=True).
            actions=set_control(control="p43_species_url", value="species"),
        ),
    ],
)

page_43 = vm.Page(
    id="page_43",
    title="Drill-through (target)",
    components=[
        vm.Graph(id="p43_graph", figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species")),
        vm.Graph(id="p43_graph_url", figure=px.scatter(df, x="petal_width", y="petal_length", color="species")),
    ],
    controls=[
        # Drill-through target restored from the store only (no URL).
        vm.Filter(id="p43_species", column="species", targets=["p43_graph"], selector=vm.Dropdown()),
        # Drill-through target that ALSO reflects its value in the URL (show_in_url=True) so it is bookmarkable.
        vm.Filter(
            id="p43_species_url",
            column="species",
            targets=["p43_graph_url"],
            selector=vm.RadioItems(),
            show_in_url=True,
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
        page_3_7,
        page_3_8,
        page_3_9,
        page_3_10,
        page_40,
        page_41,
        page_42,
        page_43,
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
                "page_3_7",
                "page_3_8",
                "page_3_9",
                "page_3_10",
            ],
            "Syncing controls across pages": ["page_40", "page_41", "page_42", "page_43"],
        }
    ),
)


if __name__ == "__main__":
    Vizro().build(dashboard).run()
