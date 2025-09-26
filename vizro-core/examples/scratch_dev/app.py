"""This is a test app to test the dashboard layout."""
import pandas as pd
from dash import ctx, html

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture
from vizro.actions import set_control
from vizro.tables import dash_ag_grid
from typing import Literal
import json


class TitledText(vm.Text):
    type: Literal["titled_text"] = "titled_text"

    title: str = ""

    def build(self):
        return html.Div(
            children=[
                html.H3(self.title) if self.title else None,
                super().build()
            ]
        )


vm.Page.add_type("components", TitledText)
vm.Container.add_type("components", TitledText)


@capture("action")
def custom_action_with_trigger(_trigger):
    return f"""```json
{json.dumps(_trigger, indent=4)}
```"""


@capture("action")
def custom_action_with_no_trigger(input_value):
    return f"""```json
{json.dumps(input_value, indent=4)}
```"""


df = px.data.iris()
df["date_column"] = pd.date_range(start=pd.to_datetime("2024-01-01"), periods=len(df), freq='D')
df["is_setosa"] = df["species"] == "setosa"

# === PAGE 1 ===

page_1 = vm.Page(
    title="Playground",
    components=[
        vm.Container(
            layout=vm.Grid(grid=[
                [0, 2],
                [1, 2],
            ]),
            variant="outlined",
            components=[
                vm.Graph(
                    id="p1_graph_1",
                    title="[Source] Graph Cross-filter",
                    figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
                    actions=[
                        set_control(control="p1_filter_1", value="species"),
                        set_control(control="p1_filter_2", value="customdata[0]"),
                        vm.Action(function=custom_action_with_trigger(), outputs="p1_text_1"),
                        vm.Action(function=custom_action_with_no_trigger("p1_graph_1.click"), outputs="p1_text_2"),
                    ],
                ),
                vm.AgGrid(
                    id="p1_ag_grid_1",
                    title="[Source] AgGrid Cross-filter",
                    figure=dash_ag_grid(df),
                    actions=[
                        set_control(control="p1_filter_1", value="species"),
                        set_control(control="p1_filter_2", value="species"),
                        vm.Action(function=custom_action_with_trigger(), outputs="p1_text_1"),
                        vm.Action(function=custom_action_with_no_trigger("p1_ag_grid_1.click"), outputs="p1_text_2"),
                    ],
                ),
                vm.Container(
                    title="[Target] Cross-filter targets",
                    layout=vm.Grid(grid=[
                        [0, 0],
                        [1, 2],
                    ]),
                    variant="outlined",
                    components=[
                        vm.AgGrid(id="p1_ag_grid_2", figure=dash_ag_grid(df)),
                        TitledText(id='p1_text_1', title="_trigger", text="""No cross-filter applied"""),
                        TitledText(id='p1_text_2', title="click", text="""No cross-filter applied""")
                    ],
                    controls=[
                        vm.Filter(id="p1_filter_1", column="species"),
                        vm.Filter(id="p1_filter_2", column="species", selector=vm.RadioItems()),
                    ],
                ),
            ],
        ),
    ]
)

# === PAGE 2 ===

page_2 = vm.Page(
    title="Graph mappings with default _trigger",
    components=[
        vm.Graph(
            id="p2_graph_1",
            figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
            actions=[
                vm.Action(function=custom_action_with_trigger(), outputs="p2_text_1"),
                vm.Action(function=custom_action_with_no_trigger("p2_graph_1.click"), outputs="p2_text_2"),
                vm.Action(function=custom_action_with_no_trigger("p2_graph_1.select"), outputs="p2_text_3"),
                vm.Action(function=custom_action_with_no_trigger("p2_graph_1.hover"), outputs="p2_text_4"),
                vm.Action(function=custom_action_with_no_trigger("p2_graph_1.zoom"), outputs="p2_text_5"),
            ],
        ),
        vm.Container(
            variant="outlined",
            layout=vm.Flex(direction="row", gap="16px"),
            components=[
                TitledText(id='p2_text_1', title="_trigger", text="""No cross-filter applied"""),
                TitledText(id='p2_text_2', title="click", text="""No cross-filter applied"""),
                TitledText(id='p2_text_3', title="select", text="""No cross-filter applied"""),
                TitledText(id='p2_text_4', title="hover", text="""No cross-filter applied"""),
                TitledText(id='p2_text_5', title="zoom", text="""No cross-filter applied"""),
            ]
        )
    ],
)

# === PAGE 3 ===

page_3 = vm.Page(
    title="AgGrid mappings with default _trigger",
    components=[
        vm.AgGrid(
            id="p3_ag_grid_1",
            figure=dash_ag_grid(df),
            actions=[
                vm.Action(function=custom_action_with_trigger(), outputs="p3_text_1"),
                vm.Action(function=custom_action_with_no_trigger("p3_ag_grid_1.click"), outputs="p3_text_2"),
                vm.Action(function=custom_action_with_no_trigger("p3_ag_grid_1.select"), outputs="p3_text_3"),
            ],
        ),
        vm.Container(
            variant="outlined",
            layout=vm.Flex(direction="row", gap="16px"),
            components=[
                TitledText(id='p3_text_1', title="_trigger", text="""No cross-filter applied"""),
                TitledText(id='p3_text_2', title="click", text="""No cross-filter applied"""),
                TitledText(id='p3_text_3', title="select", text="""No cross-filter applied"""),
            ]
        )
    ],
)


# === PAGE 4 ===

@capture("action")
def custom_action_with_trigger_and_multiple_inputs(click, select, hover=None, zoom=None, _trigger=None):
    return f"""```json
CLICK:
{json.dumps(click, indent=4)}

SELECT:
{json.dumps(select, indent=4)}

HOVER:
{json.dumps(hover, indent=4) if hover else "NO HOVER DATA"}

ZOOM:
{json.dumps(zoom, indent=4) if zoom else "NO ZOOM DATA"}

_TRIGGER:
{json.dumps(_trigger, indent=4)}
```"""


page_4 = vm.Page(
    title="[multiple outputs] Graph mappings with default _trigger",
    components=[
        vm.Graph(
            id="p4_graph_1",
            figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
            actions=[
                vm.Action(
                    function=custom_action_with_trigger_and_multiple_inputs(
                        "p4_graph_1.click",
                        "p4_graph_1.select",
                        "p4_graph_1.hover",
                        "p4_graph_1.zoom",
                    ),
                    outputs="p4_text_1"
                ),
            ],
        ),
        TitledText(id='p4_text_1', title="click, select, hover, zoom, _trigger", text="""No cross-filter applied"""),
    ],
)


# === PAGE 5 ===
page_5 = vm.Page(
    title="[multiple outputs] AgGrid mappings with default _trigger",
    components=[
        vm.AgGrid(
            id="p5_ag_grid_1",
            figure=dash_ag_grid(df),
            actions=[
                vm.Action(
                    function=custom_action_with_trigger_and_multiple_inputs(
                        "p5_ag_grid_1.click",
                        "p5_ag_grid_1.select",
                    ),
                    outputs="p5_text_1"
                ),
            ],
        ),
        TitledText(id='p5_text_1', title="click, select, _trigger", text="""No cross-filter applied"""),
    ],
)


# === PAGE 6 ===

page_6 = vm.Page(
    title="Different Graph triggers",
    layout=vm.Grid(grid=[
        [0, 1, 2, 3, 4],
        [5, 5, 5, 5, 5],
    ]),
    components=[
        vm.Graph(
            id="p6_graph_1",
            title="Default trigger",
            figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
            actions=vm.Action(function=custom_action_with_trigger(), outputs="p6_text_1")
        ),
        vm.Graph(
            id="p6_graph_2",
            title="click",
            figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
            action_trigger="click",
            actions=vm.Action(function=custom_action_with_trigger(), outputs="p6_text_2")
        ),
        vm.Graph(
            id="p6_graph_3",
            title="select",
            figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
            action_trigger="select",
            actions=vm.Action(function=custom_action_with_trigger(), outputs="p6_text_3")
        ),
        vm.Graph(
            id="p6_graph_4",
            title="hover",
            figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
            action_trigger="hover",
            actions=vm.Action(function=custom_action_with_trigger(), outputs="p6_text_4")
        ),
        vm.Graph(
            id="p6_graph_5",
            title="zoom",
            figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
            action_trigger="zoom",
            actions=vm.Action(function=custom_action_with_trigger(), outputs="p6_text_5")
        ),
        vm.Container(
            variant="outlined",
            layout=vm.Flex(direction="row", gap="16px"),
            components=[
                TitledText(id='p6_text_1', title="_trigger", text="""No cross-filter applied"""),
                TitledText(id='p6_text_2', title="click", text="""No cross-filter applied"""),
                TitledText(id='p6_text_3', title="select", text="""No cross-filter applied"""),
                TitledText(id='p6_text_4', title="hover", text="""No cross-filter applied"""),
                TitledText(id='p6_text_5', title="zoom", text="""No cross-filter applied"""),
            ]
        )
    ]
)

# # === Page 7 ===

page_7 = vm.Page(
    title="Different AgGrid triggers",
    layout=vm.Grid(grid=[
        [0, 1, 2],
        [3, 3, 3],
    ]),
    components=[
        vm.AgGrid(
            id="p7_ag_grid_1",
            title="Default trigger",
            figure=dash_ag_grid(df),
            actions=vm.Action(function=custom_action_with_trigger(), outputs="p7_text_1")
        ),
        vm.AgGrid(
            id="p7_ag_grid_2",
            title="click",
            figure=dash_ag_grid(df),
            action_trigger="click",
            actions=vm.Action(function=custom_action_with_trigger(), outputs="p7_text_2")
        ),
        vm.AgGrid(
            id="p7_ag_grid_3",
            title="select",
            figure=dash_ag_grid(df, dashGridOptions={"rowSelection": {"mode": "multiRow"}}),
            action_trigger="select",
            actions=vm.Action(function=custom_action_with_trigger(), outputs="p7_text_3")
        ),
        vm.Container(
            variant="outlined",
            layout=vm.Flex(direction="row", gap="16px"),
            components=[
                TitledText(id='p7_text_1', title="_trigger", text="""No cross-filter applied"""),
                TitledText(id='p7_text_2', title="click", text="""No cross-filter applied"""),
                TitledText(id='p7_text_3', title="select", text="""No cross-filter applied"""),
            ]
        )
    ]
)

# === Page 8 ===

page_8 = vm.Page(
    title="Graph targets different selectors",
    components=[
        vm.Graph(
            id="p8_graph_1",
            figure=px.scatter(
                df, x="sepal_width", y="sepal_length", color="species",
                custom_data=["species", "sepal_length", "date_column", "is_setosa"],
            ),
            actions=[
                set_control(control="p8_filter_1", value="species"),
                set_control(control="p8_filter_2", value="species"),
                set_control(control="p8_filter_3", value="species"),
                set_control(control="p8_filter_4", value="species"),
                # TODO Q AM: Can we fetch the action.value from the vm.Filter.column?
                #  This would make the action.value as optional argument for both Graph and AgGrid?
                # set_control(control="p8_filter_5", value="sepal_length"),
            ],
        ),
        vm.Graph(
            id="p8_graph_target",
            figure=px.scatter(df, x="sepal_width", y="petal_length", color="species", custom_data=["species"]),
        )
    ],
    controls=[
        # Categorical Single
        vm.Filter(id="p8_filter_1", targets=["p8_graph_target"], column="species", selector=vm.RadioItems()),
        vm.Filter(id="p8_filter_2", targets=["p8_graph_target"], column="species", selector=vm.Dropdown(multi=False)),
        # Categorical Multi
        vm.Filter(id="p8_filter_3", targets=["p8_graph_target"], column="species", selector=vm.Checklist()),
        vm.Filter(id="p8_filter_4", targets=["p8_graph_target"], column="species", selector=vm.Dropdown()),
        # Numeric Single
        vm.Filter(id="p8_filter_5", targets=["p8_graph_target"], column="sepal_length", selector=vm.Slider()),
        # Numeric Range
        vm.Filter(id="p8_filter_6", targets=["p8_graph_target"], column="sepal_length", selector=vm.RangeSlider()),
        # Temporal Single
        vm.Filter(id="p8_filter_7", targets=["p8_graph_target"], column="date_column", selector=vm.DatePicker(range=False)),
        # Temporal Range
        vm.Filter(id="p8_filter_8", targets=["p8_graph_target"], column="date_column", selector=vm.DatePicker(range=True)),
        # Boolean Single
        vm.Filter(id="p8_filter_9", targets=["p8_graph_target"], column="is_setosa", selector=vm.Switch()),
    ]
)

dashboard = vm.Dashboard(pages=[page_1, page_2, page_3, page_4, page_5, page_6, page_7, page_8])

# TODO: Make it work for multiple selector outputs.

# TODO: Check page_3 and page_4 and how well the code extract different properties for the same input ID.
#       Check the TODO in the action.py where this "brittle" behaviour is explained

# TODO: Fix the app so it display the represented feature more clearly.

# TODO: Streamline the actions props

if __name__ == "__main__":
    Vizro().build(dashboard).run()
