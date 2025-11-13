"""Dev app to try things out."""

import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
from vizro.managers import model_manager

import vizro.actions as va
from vizro.models.types import capture
from vizro.tables import dash_ag_grid
from typing import Any
from box import Box
import dash

# TODO NOW PP:
#  DONE: PoC
#  DONE: Move implementation to vm.Graph and va.set_control
#  0. See other TODOs NOW PP.
#  1. Add support for area charts via `vizroSelectedData.data` dcc.Store
#  2. Handle empty selection and (box select on nothing) and reseting selection (double click on the same point)
#  3. Test with other graph.set_control.value syntax like "customdata[0]"
#  4. See how to handle different control types (same and different page(add more drill-through examples))
#  5. See how to handle resetting drill-through
#  6. See whether to return values[-1] instead of values[0] when many points selected but a single-select control is targeted.
#  7. hrt + hrl
#  8. Add more unit tests
#  9. Add more e2e tests


page_1 = vm.Page(
    title="set_control ",
    components=[
        vm.Graph(
            figure=px.bar(px.data.iris(), x="sepal_width", y="sepal_length", color="species", custom_data="species"),
            actions=[
                va.set_control(control="p1_filter_1", value="customdata[0]"),
                va.set_control(control="p1_filter_2", value="species"),
                va.set_control(control="p1_filter_3", value="species"),
                va.set_control(control="p1_filter_4", value="species"),
            ]
        ),
        vm.AgGrid(id="table", figure=dash_ag_grid(px.data.iris())),
    ],
    controls=[
        vm.Filter(
            id="p1_filter_1",
            column="species",
            targets=["table"],
            selector=vm.Dropdown(multi=True),
        ),
        vm.Filter(
            id="p1_filter_2",
            column="species",
            targets=["table"],
            selector=vm.Dropdown(multi=False),
        ),
        vm.Filter(
            id="p1_filter_3",
            column="species",
            targets=["table"],
            selector=vm.Dropdown(value=["virginica", "versicolor"], multi=True),
        ),
        vm.Filter(
            id="p1_filter_4",
            column="species",
            targets=["table"],
            selector=vm.Dropdown(value="virginica", multi=False),
        )
    ],
)


page_2 = vm.Page(
    title="Drill-through source page",
    components=[
        vm.Graph(
            figure=px.bar(px.data.iris(), x="sepal_width", y="sepal_length", color="species", custom_data="species"),
            actions=va.set_control(control="p3_filter_1", value="species"),
        ),
    ],
)

page_3 = vm.Page(
    title="Drill-through target page",
    components=[
        vm.AgGrid(figure=dash_ag_grid(px.data.iris())),
    ],
    controls=[vm.Filter(id="p3_filter_1", column="species", show_in_url=True)],
)


dashboard = vm.Dashboard(pages=[page_1, page_2, page_3])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
