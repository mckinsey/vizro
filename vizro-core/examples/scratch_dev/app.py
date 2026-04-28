"""This is a test app to test the dashboard layout."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture
from vizro.managers import data_manager
from vizro.actions import update_figures


df = px.data.iris()
data_manager["dynamic_iris"] = lambda number_of_points=10: df.head(number_of_points)


SPECIES_COLORS = {"setosa": "#00b4ff", "versicolor": "#ff9222", "virginica": "#3949ab"}


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

dashboard = vm.Dashboard(pages=[page_0_1, page_1_1, page_2_1])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
