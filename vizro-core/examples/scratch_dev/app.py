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
            actions_trigger="click",
            actions=vm.Action(function=custom_action_with_trigger(), outputs="p6_text_2")
        ),
        vm.Graph(
            id="p6_graph_3",
            title="select",
            figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
            actions_trigger="select",
            actions=vm.Action(function=custom_action_with_trigger(), outputs="p6_text_3")
        ),
        vm.Graph(
            id="p6_graph_4",
            title="hover",
            figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
            actions_trigger="hover",
            actions=vm.Action(function=custom_action_with_trigger(), outputs="p6_text_4")
        ),
        vm.Graph(
            id="p6_graph_5",
            title="zoom",
            figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
            actions_trigger="zoom",
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
            actions_trigger="click",
            actions=vm.Action(function=custom_action_with_trigger(), outputs="p7_text_2")
        ),
        vm.AgGrid(
            id="p7_ag_grid_3",
            title="select",
            figure=dash_ag_grid(df, dashGridOptions={"rowSelection": {"mode": "multiRow"}}),
            actions_trigger="select",
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


# TODO Q AM: Let's think about should we make this clickmode the default for Graph or just explain how it can be used?
@capture("graph")
def clickmode_fig(data_frame, **kwargs):
    fig = px.scatter(df, **kwargs)
    fig.update_layout(clickmode="event+select")
    return fig


page_8_fig = px.scatter(
    data_frame=df, x="sepal_width", y="sepal_length", color="species",
    custom_data=["species", "sepal_length", "date_column", "is_setosa"],
    hover_data=["species", "sepal_length", "date_column", "is_setosa"],
)


page_8 = vm.Page(
    title="Graph targets different selectors",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Click set_control",
                    components=[
                        vm.Graph(
                            figure=page_8_fig,
                            title="Click on points to set the filters below",
                            actions=[
                                # TODO Q AM: Can we fetch the action.value from the vm.Filter.column?
                                #  This would make the action.value as optional argument for both Graph and AgGrid?
                                set_control(control="p8_filter_click_1", value="species"),
                                set_control(control="p8_filter_click_2", value="species"),
                                set_control(control="p8_filter_click_3", value="species"),
                                set_control(control="p8_filter_click_4", value="species"),
                                set_control(control="p8_filter_click_5", value="sepal_length"),
                                set_control(control="p8_filter_click_6", value="sepal_length"),
                                set_control(control="p8_filter_click_7", value="date_column"),
                                set_control(control="p8_filter_click_8", value="date_column"),
                                set_control(control="p8_filter_click_9", value="is_setosa"),
                            ],
                        ),
                        vm.Container(
                            components=[
                                vm.Graph(figure=px.scatter(df, x="sepal_width", y="petal_length", color="species")),
                            ],
                            controls=[
                                # Categorical-Single
                                vm.Filter(id="p8_filter_click_1", column="species", selector=vm.RadioItems()),
                                vm.Filter(id="p8_filter_click_2", column="species", selector=vm.Dropdown(multi=False)),
                                # Categorical-Multi
                                vm.Filter(id="p8_filter_click_3", column="species", selector=vm.Checklist()),
                                vm.Filter(id="p8_filter_click_4", column="species", selector=vm.Dropdown()),
                                # Numeric-Single
                                vm.Filter(id="p8_filter_click_5", column="sepal_length", selector=vm.Slider()),
                                # Numeric-Range
                                vm.Filter(id="p8_filter_click_6", column="sepal_length", selector=vm.RangeSlider()),
                                # Temporal-Single
                                vm.Filter(id="p8_filter_click_7", column="date_column", selector=vm.DatePicker(range=False)),
                                # Temporal-Range
                                vm.Filter(id="p8_filter_click_8", column="date_column", selector=vm.DatePicker(range=True)),
                                # Boolean Single
                                vm.Filter(id="p8_filter_click_9", column="is_setosa", selector=vm.Switch()),
                            ]
                        ),
                    ]
                ),
                vm.Container(
                    title="Select set_control",
                    components=[
                        vm.Graph(
                            figure=page_8_fig,
                            title="Select graph points to set the filters below",
                            actions_trigger="select",
                            actions=[
                                set_control(control="p8_filter_select_1", value="species"),
                                set_control(control="p8_filter_select_2", value="species"),
                                set_control(control="p8_filter_select_3", value="sepal_length"),
                                set_control(control="p8_filter_select_4", value="date_column"),
                            ]
                        ),
                        vm.Container(
                            components=[
                                vm.Graph(figure=px.scatter(df, x="sepal_width", y="petal_length", color="species")),
                            ],
                            controls=[
                                # Categorical Multi
                                vm.Filter(id="p8_filter_select_1", column="species", selector=vm.Checklist()),
                                vm.Filter(id="p8_filter_select_2", column="species", selector=vm.Dropdown()),
                                # Numeric Range
                                vm.Filter(id="p8_filter_select_3", column="sepal_length", selector=vm.RangeSlider()),
                                # Temporal Range
                                vm.Filter(id="p8_filter_select_4", column="date_column", selector=vm.DatePicker(range=True)),
                            ]
                        )
                    ]
                ),
                # TODO: Add hover tab
                # TODO: Add zoom tab
            ]
        ),
    ],
)

page_9 = vm.Page(
    title="AgGrid targets different selectors",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Click set_control",
                    components=[
                        vm.AgGrid(
                            figure=dash_ag_grid(df),
                            title="Click on row to set the filters below",
                            actions=[
                                set_control(control="p9_filter_click_1", value="species"),
                                set_control(control="p9_filter_click_2", value="species"),
                                set_control(control="p9_filter_click_3", value="species"),
                                set_control(control="p9_filter_click_4", value="species"),
                                set_control(control="p9_filter_click_5", value="sepal_length"),
                                set_control(control="p9_filter_click_6", value="sepal_length"),
                                set_control(control="p9_filter_click_7", value="date_column"),
                                set_control(control="p9_filter_click_8", value="date_column"),
                                set_control(control="p9_filter_click_9", value="is_setosa"),
                            ],
                        ),
                        vm.Container(
                            components=[
                                vm.Graph(figure=px.scatter(df, x="sepal_width", y="petal_length", color="species")),
                            ],
                            controls=[
                                vm.Filter(id="p9_filter_click_1", column="species", selector=vm.RadioItems()),
                                vm.Filter(id="p9_filter_click_2", column="species", selector=vm.Dropdown(multi=False)),
                                vm.Filter(id="p9_filter_click_3", column="species", selector=vm.Checklist()),
                                vm.Filter(id="p9_filter_click_4", column="species", selector=vm.Dropdown()),
                                vm.Filter(id="p9_filter_click_5", column="sepal_length", selector=vm.Slider()),
                                vm.Filter(id="p9_filter_click_6", column="sepal_length", selector=vm.RangeSlider()),
                                vm.Filter(id="p9_filter_click_7", column="date_column",
                                          selector=vm.DatePicker(range=False)),
                                vm.Filter(id="p9_filter_click_8", column="date_column",
                                          selector=vm.DatePicker(range=True)),
                                vm.Filter(id="p9_filter_click_9", column="is_setosa", selector=vm.Switch()),
                            ]
                        ),
                    ]
                ),
                vm.Container(
                    title="Select set_control",
                    components=[
                        vm.AgGrid(
                            figure=dash_ag_grid(df, dashGridOptions={"rowSelection": {"mode": "multiRow"}}),
                            title="Select table rows to set the filters below",
                            actions_trigger="select",
                            actions=[
                                set_control(control="p9_filter_select_1", value="species"),
                                set_control(control="p9_filter_select_2", value="species"),
                                set_control(control="p9_filter_select_3", value="sepal_length"),
                                set_control(control="p9_filter_select_4", value="date_column"),
                            ]
                        ),
                        vm.Container(
                            components=[
                                vm.Graph(figure=px.scatter(df, x="sepal_width", y="petal_length", color="species")),
                            ],
                            controls=[
                                vm.Filter(id="p9_filter_select_1", column="species", selector=vm.Checklist()),
                                vm.Filter(id="p9_filter_select_2", column="species", selector=vm.Dropdown()),
                                vm.Filter(id="p9_filter_select_3", column="sepal_length", selector=vm.RangeSlider()),
                                vm.Filter(id="p9_filter_select_4", column="date_column", selector=vm.DatePicker(range=True)),
                            ]
                        )
                    ]
                ),
            ]
        ),
    ],
)

# TODO: HOW ABOUT to have one transformer of input per model (one method per model), and one set_control output mapper function.
#   This would be actions-info extraction_inputs function + _adjust_result_by_control_type combined.
#   Have on mind and check whether multiple portions of info could be propagated through the action input and trigger. (enabling multiple with that triggers??)
#     I'm talking about dict format dash callback State/Input (something similar that's used for old filter_interaction)

dashboard = vm.Dashboard(pages=[page_1, page_2, page_3, page_4, page_5, page_6, page_7, page_8, page_9])

# TODO: Make it work for multiple selector outputs.
#  1. make that _get_value_from_trigger works for different selector outputs.
#    1.1. Could value be out of range/options of the targeted selector? SET p8_graph_target.df.head(5) and see.
#        Seems like it works except checklist_select_all.
#  2. Think about do we need two place of the similar extraction logic:
#   - from _action callback calling calling the MODEL._action_trigger_extractions
#   - from set_controls calling the MODEL._get_value_from_trigger
#   - from set_controls calling the MODEL._adjust_result_by_control_type
#  Potential solution:
#  1. Leave click/select and other _action_inputs and _action_triggers
#  2. Delete _action_trigger_extractions (we don't get much from this.. see simple lambda functions that don't do much)
#  3. Do conversion in _get_value_from_trigger for converting inputs to final look like [min_value, max_value]

# TODO: Check page_3 and page_4 and how well the code extract different properties for the same input ID.
#  Check the TO-DO in the action.py where this "brittle" behaviour is explained

# TODO: Streamline the actions props

if __name__ == "__main__":
    Vizro().build(dashboard).run()
