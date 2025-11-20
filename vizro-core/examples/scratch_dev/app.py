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
#  DONE: 0. Check whether custom_data=["species"] vs custom_data="species" works the same for are chart for example.
#  DONE: 0. Test pieChart.
#     DONE: 0.1. Try to send a flag about the chart type to CS-CB function so we can handle area/line/pie chart properly.
#          Currently, I can't differentiate false clickData from bar chart and real clickData from pie chart...
#     DONE: 0.2. Add more scratch examples.
#     DONE: 0.2. Try to whether this solves the problem when the `clickmode="event"` is manually set.
#  DONE: 0. Check when graph1->sc->graph2->sc->graph1 are chained.
#  DONE: 1. Refactor vm.Graph._get_value_from_trigger code.
#  DONE: 1. Add support for area charts via `vizroSelectedData.data` dcc.Store
#  DONE: 2. Handle empty selection and (box select on nothing) and resetting selection (double click on the same point)
#    DONE 2.1. Do same for AgGrid a
#    DONE 2.2. Add more examples in scratch
#  DONE: 3. Test with other graph.set_control.value syntax like "customdata[0]"
#  DONE: 4. See how to handle different control types (same and different page)
#    DONE: 4.1. Add more drill-through examples in scratch
#  DONE 5. See how to handle resetting drill-through
#  DONE: 6. See does it work if the "clickmode" is turned off.
#  DONE: 7. Test with Button(None, [], 123, [1,2,3], "123")
#    DONE: 7.1. Add more example in scratch for same and different page.
#  8. hrt + hrl
#  8. Test custom_data=["x"]
#  9. Add more unit tests
#  10. Add more e2e tests
#  11. Explain what charts don't support selectedData so I made a custom solution for them.


# TODO AM OQ: I handled single-select controls like this:
#  1. Graph/AgGrid setting None or [] is treated as None -> reset control
#  2. Figure/Button/Card setting None -> reset control
#  3. Figure/Button/Card setting []
#     3.1. to multi-select control: sets [] (as expected)
#     3.2. to single-select control: no_update
#  4. Very soon we'll enable set_control filter -> filter. In that case how Checklist=[] -> RadioItems would be treated?
#     I think the same as 3 (do no_update). Is that ok? Why don't we treat graph/ag-grid empty selection the same way??


def _create_filters(prefix: str):
    return [
        vm.Filter(
            id=f"{prefix}filter_1",
            column="species",
            targets=[f"{prefix}table"],
            selector=vm.Dropdown(multi=True),
        ),
        vm.Filter(
            id=f"{prefix}filter_2",
            column="species",
            targets=[f"{prefix}table"],
            selector=vm.Dropdown(multi=False),
        ),
        vm.Filter(
            id=f"{prefix}filter_3",
            column="species",
            targets=[f"{prefix}table"],
            selector=vm.Dropdown(value=["virginica", "versicolor"], multi=True),
        ),
        vm.Filter(
            id=f"{prefix}filter_4",
            column="species",
            targets=[f"{prefix}table"],
            selector=vm.Dropdown(value="virginica", multi=False),
        )
    ]


pre = "p1_"
page_1 = vm.Page(
    title="set_control from bar",
    components=[
        vm.Graph(
            figure=px.bar(px.data.iris(), x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
            actions=[
                va.set_control(control=f"{pre}filter_1", value="customdata[0]"),
                va.set_control(control=f"{pre}filter_2", value="customdata[0]"),
                va.set_control(control=f"{pre}filter_3", value="species"),
                va.set_control(control=f"{pre}filter_4", value="species"),
            ]
        ),
        vm.AgGrid(id=f"{pre}table", figure=dash_ag_grid(px.data.iris())),
    ],
    controls=_create_filters(prefix=pre)
)

pre = "p2_"
page_2 = vm.Page(
    title="set_control from charts (area/pie/line...)",
    layout=vm.Grid(grid=[[0], [0], [1]]),
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Common charts",
                    layout=vm.Grid(grid=[[0, 1], [2, 3]]),
                    components=[
                        vm.Graph(
                            figure=px.area(px.data.iris(), x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
                            actions=[
                                va.set_control(control=f"{pre}filter_1", value="customdata[0]"),
                                va.set_control(control=f"{pre}filter_2", value="customdata[0]"),
                                va.set_control(control=f"{pre}filter_3", value="species"),
                                va.set_control(control=f"{pre}filter_4", value="species"),
                            ]
                        ),
                        vm.Graph(
                            figure=px.pie(px.data.iris(), names="species", values="sepal_length", custom_data=["species"]),
                            actions=[
                                va.set_control(control=f"{pre}filter_1", value="customdata[0]"),
                                va.set_control(control=f"{pre}filter_2", value="customdata[0]"),
                                va.set_control(control=f"{pre}filter_3", value="species"),
                                va.set_control(control=f"{pre}filter_4", value="species"),
                            ]
                        ),
                        vm.Graph(
                            figure=px.line(px.data.iris(), x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
                            actions=[
                                va.set_control(control=f"{pre}filter_1", value="customdata[0]"),
                                va.set_control(control=f"{pre}filter_2", value="customdata[0]"),
                                va.set_control(control=f"{pre}filter_3", value="species"),
                                va.set_control(control=f"{pre}filter_4", value="species"),
                            ]
                        ),
                        vm.Graph(
                            figure=px.funnel_area(px.data.iris(), names="species", values="sepal_length", custom_data=["species"]),
                            actions=[
                                va.set_control(control=f"{pre}filter_1", value="customdata[0]"),
                                va.set_control(control=f"{pre}filter_2", value="customdata[0]"),
                                va.set_control(control=f"{pre}filter_3", value="species"),
                                va.set_control(control=f"{pre}filter_4", value="species"),
                            ],
                        )
                    ]
                ),
                vm.Container(
                    title="Rare charts",
                    layout=vm.Grid(grid=[[0, 1], [2, 3]]),
                    components=[
                        vm.Graph(
                            title="IMPORTANT: Does not support custom_data.",
                            figure=px.density_heatmap(
                                px.data.iris(), x="sepal_width", y="sepal_length",
                            ),
                            actions=[
                                va.set_control(control=f"{pre}filter_1", value="customdata[0]"),
                                va.set_control(control=f"{pre}filter_2", value="customdata[0]"),
                                va.set_control(control=f"{pre}filter_3", value="species"),
                                va.set_control(control=f"{pre}filter_4", value="species"),
                            ],
                        ),
                        vm.Graph(
                            figure=px.line_polar(px.data.iris(), r="sepal_length", theta="species", color="species", custom_data=["species"]),
                            actions=[
                                va.set_control(control=f"{pre}filter_1", value="customdata[0]"),
                                va.set_control(control=f"{pre}filter_2", value="customdata[0]"),
                                va.set_control(control=f"{pre}filter_3", value="species"),
                                va.set_control(control=f"{pre}filter_4", value="species"),
                            ],
                        ),
                        vm.Graph(
                            figure=px.treemap(px.data.iris(), path=["species"], values="sepal_length", custom_data=["species"]),
                            actions=[
                                va.set_control(control=f"{pre}filter_1", value="customdata[0]"),
                                va.set_control(control=f"{pre}filter_2", value="customdata[0]"),
                                va.set_control(control=f"{pre}filter_3", value="species"),
                                va.set_control(control=f"{pre}filter_4", value="species"),
                            ],
                        ),
                        vm.Graph(
                            title="IMPORTANT: Does not support custom_data nor clickData :D",
                            figure=px.parallel_coordinates(px.data.iris(), color="sepal_length", dimensions=["sepal_width", "sepal_length", "petal_width", "petal_length"]),
                            actions=[
                                va.set_control(control=f"{pre}filter_1", value="customdata[0]"),
                                va.set_control(control=f"{pre}filter_2", value="customdata[0]"),
                                va.set_control(control=f"{pre}filter_3", value="species"),
                                va.set_control(control=f"{pre}filter_4", value="species"),
                            ],
                        )
                    ]
                ),
            ]
        ),
        vm.AgGrid(id=f"{pre}table", figure=dash_ag_grid(px.data.iris())),
    ],
    controls=_create_filters(prefix=pre)
)

pre = "p3_"
page_3 = vm.Page(
    title="set_control from ag-grid",
    components=[
        vm.AgGrid(
            figure=dash_ag_grid(px.data.iris().iloc[[0, 1, 50, 51, 100, 101]]),
            actions=[
                va.set_control(control=f"{pre}filter_1", value="species"),
                va.set_control(control=f"{pre}filter_2", value="species"),
                va.set_control(control=f"{pre}filter_3", value="species"),
                va.set_control(control=f"{pre}filter_4", value="species"),
            ]
        ),
        vm.AgGrid(id=f"{pre}table", figure=dash_ag_grid(px.data.iris())),
    ],
    controls=_create_filters(prefix=pre)
)

pre = "p4_"
page_4 = vm.Page(
    title="set_control None/[]/str/[str] from button/card",
    components=[
        vm.Button(
            text="Set None",
            actions=[
                va.set_control(control=f"{pre}filter_1", value=None),
                va.set_control(control=f"{pre}filter_2", value=None),
                va.set_control(control=f"{pre}filter_3", value=None),
                va.set_control(control=f"{pre}filter_4", value=None),
            ]
        ),
        vm.Button(
            text="Set []",
            actions=[
                va.set_control(control=f"{pre}filter_1", value=[]),
                va.set_control(control=f"{pre}filter_2", value=[]),
                va.set_control(control=f"{pre}filter_3", value=[]),
                va.set_control(control=f"{pre}filter_4", value=[]),
            ]
        ),
        vm.Card(
            text="Set 'versicolor'",
            actions=[
                va.set_control(control=f"{pre}filter_1", value="versicolor"),
                va.set_control(control=f"{pre}filter_2", value="versicolor"),
                va.set_control(control=f"{pre}filter_3", value="versicolor"),
                va.set_control(control=f"{pre}filter_4", value="versicolor"),
            ]
        ),
        vm.Card(
            text="""Set [['setosa', 'versicolor']]""",
            actions=[
                va.set_control(control=f"{pre}filter_1", value=["setosa", "versicolor"]),
                va.set_control(control=f"{pre}filter_2", value=["setosa", "versicolor"]),
                va.set_control(control=f"{pre}filter_3", value=["setosa", "versicolor"]),
                va.set_control(control=f"{pre}filter_4", value=["setosa", "versicolor"]),
            ]
        ),
        vm.AgGrid(id=f"{pre}table", figure=dash_ag_grid(px.data.iris())),
    ],
    controls=_create_filters(prefix=pre),
)

pre = "p5_"
pre_target = "p6_"
page_5 = vm.Page(
    title="Drill-through source page",
    layout=vm.Grid(grid=[[0, 1]]),
    components=[
        vm.Container(
            title="Set multi-select",
            layout=vm.Flex(),
            components=[
                vm.Graph(
                    figure=px.bar(px.data.iris(), x="sepal_width", y="sepal_length", color="species",
                                  custom_data=["species"]),
                    actions=va.set_control(control=f"{pre_target}filter_1", value="species"),
                ),
                vm.Button(
                    text="Set None",
                    actions=va.set_control(control=f"{pre_target}filter_1", value=None),
                ),
                vm.Button(
                    text="Set []",
                    actions=va.set_control(control=f"{pre_target}filter_1", value=[]),
                ),
                vm.Card(
                    text="Set 'versicolor'",
                    actions=va.set_control(control=f"{pre_target}filter_1", value="versicolor"),
                ),
                vm.Card(
                    text="""Set [['setosa', 'versicolor']]""",
                    actions=va.set_control(control=f"{pre_target}filter_1", value=["setosa", "versicolor"]),
                ),
            ]
        ),
        vm.Container(
            title="Set single-select",
            layout=vm.Flex(),
            components=[
                vm.Graph(
                    figure=px.bar(px.data.iris(), x="sepal_width", y="sepal_length", color="species",
                                  custom_data=["species"]),
                    actions=va.set_control(control=f"{pre_target}filter_2", value="species"),
                ),
                vm.Button(
                    text="Set None",
                    actions=va.set_control(control=f"{pre_target}filter_2", value=None),
                ),
                vm.Button(
                    text="Set []",
                    actions=va.set_control(control=f"{pre_target}filter_2", value=[]),
                ),
                vm.Card(
                    text="Set 'versicolor'",
                    actions=va.set_control(control=f"{pre_target}filter_2", value="versicolor"),
                ),
                vm.Card(
                    text="""Set [['setosa', 'versicolor']]""",
                    actions=va.set_control(control=f"{pre_target}filter_2", value=["setosa", "versicolor"]),
                ),
            ]
        )
    ],

)
page_6 = vm.Page(
    title="Drill-through target page",
    components=[
        vm.AgGrid(figure=dash_ag_grid(px.data.iris())),
    ],
    controls=[
        vm.Filter(
            id=f"{pre_target}filter_1",
            column="species",
            show_in_url=True
        ),
        vm.Filter(
            id=f"{pre_target}filter_2",
            column="species",
            show_in_url=True,
            selector=vm.Dropdown(multi=False),
        )
    ],
)


pre = "p7_"
page_7 = vm.Page(
    title="Old filter_interaction",
    components=[
        vm.Graph(
            figure=px.scatter(px.data.iris(), x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
            actions=va.filter_interaction(targets=[f"{pre}table"])
        ),
        vm.AgGrid(id=f"{pre}table", figure=dash_ag_grid(px.data.iris())),
    ],
)

pre = "p8_"
page_8 = vm.Page(
    title="Self-filtering graph",
    components=[
        vm.Graph(
            id=f"{pre}graph_1",
            figure=px.scatter(px.data.iris(), x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
            actions=va.set_control(control=f"{pre}filter_1", value="customdata[0]"),
        ),
    ],
    controls=[
        vm.Filter(
            id=f"{pre}filter_1",
            column="species",
        )
    ]
)


dashboard = vm.Dashboard(pages=[page_1, page_2, page_3, page_4, page_5, page_6, page_7, page_8])

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
