"""This is a test app to test the dashboard layout."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager
from vizro.actions import update_targets


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
                # An empty actions list opts out of the default "refresh on change" behavior.
                actions=[],
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
                actions=[],
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

page_3_1 = vm.Page(
    id="page_3_1",
    title="Refresh filters with a slider, apply them with a button",
    components=[
        vm.Graph(
            id="p31_graph",
            figure=px.scatter(
                "dynamic_iris", x="sepal_width", y="sepal_length", color="species", color_discrete_map=SPECIES_COLORS
            ),
        ),
    ],
    controls=[
        vm.Parameter(
            id="p31_master_slider",
            targets=["p31_graph.data_frame.number_of_points"],
            selector=vm.Slider(
                min=10,
                max=150,
                step=10,
                value=10,
                title="Change me to resize the data and refresh the two filters below (graph is not redrawn).",
                actions=update_targets(targets=["p31_radio_filter", "p31_range_filter"]),
            ),
        ),
        vm.Filter(
            id="p31_radio_filter",
            column="species",
            targets=["p31_graph"],
            selector=vm.RadioItems(
                title="Options refreshed by the slider; does NOT auto-apply.",
                actions=[],
            ),
        ),
        vm.Filter(
            id="p31_range_filter",
            column="petal_length",
            targets=["p31_graph"],
            selector=vm.RangeSlider(
                title="min/max refreshed by the slider; does NOT auto-apply.",
                actions=[],
            ),
        ),
        vm.Button(text="Apply filters", actions=update_targets(targets=["p31_graph"])),
    ],
)

# ====== **NEW** A deferred data_frame Parameter is still applied when its targets are refreshed ======
# The Parameter (Slider) resizes the graph's data but has `actions=[]`, so changing it does nothing on its own. The
# Filter is likewise deferred (`actions=[]`). Clicking the Button refreshes the whole page (bare `update_targets()`):
# the graph reloads with the new data size AND the filter's options recompute to match - proving the deferred
# parameter's value is counted even though it never triggered a refresh itself.

page_4_1 = vm.Page(
    id="page_4_1",
    title="Deferred parameter is still applied on refresh",
    components=[
        vm.Graph(
            id="p41_graph",
            figure=px.scatter(
                "dynamic_iris", x="sepal_width", y="sepal_length", color="species", color_discrete_map=SPECIES_COLORS
            ),
        ),
    ],
    controls=[
        vm.Parameter(
            id="p41_parameter",
            targets=["p41_graph.data_frame.number_of_points"],
            selector=vm.Slider(
                min=10,
                max=150,
                step=10,
                value=10,
                title="Resizes the data but does NOT auto-apply; its value is honored on the next refresh.",
                actions=[],
            ),
        ),
        vm.Filter(
            id="p41_filter",
            column="species",
            targets=["p41_graph"],
            selector=vm.RadioItems(
                title="Dynamic filter; options recompute from the resized data on refresh.",
                actions=[],
            ),
        ),
        vm.Button(text="Refresh Filter", actions=update_targets(targets=["p41_filter"])),
        vm.Button(text="Refresh Graph", actions=update_targets(targets=["p41_graph"])),
    ],
)


dashboard = vm.Dashboard(
    pages=[
        page_0_1,
        page_1_1,
        page_2_1,
        page_3_1,
        page_4_1,
    ]
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
