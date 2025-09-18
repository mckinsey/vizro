import vizro.actions as va
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid

tips = px.data.tips()


df = px.data.iris()
df_gapminder = px.data.gapminder()[px.data.gapminder().year == 2007]


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
                va.set_control(control="total_bill_filter", value="x"),
                va.set_control(control="tip_filter", value="y"),
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
                    # TODO: The order of actions was: SC-1 → SC-2 → FA-1 → SC-3 → FA-2 → SC-4 → FA-3 → FA-4
                    #  - Could it cause a real problem? NO. As filter actions update all targets they adjust. ✅
                    #  - Hence, I’d remove the experimental.
                    #  - One of the ways to patch it: in the action definition add `stop: bool = False`. If it's True,
                    #       call dash.set_props(target.guard; True)
                    #  - What's the optimal solution: -> set_controls + update_figures (only 2 http requests)
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
        vm.AgGrid(id="tips_table", figure=dash_ag_grid(tips)),  # (1)!
    ],
    controls=[
        vm.Filter(id="total_bill_filter", column="total_bill", targets=["tips_table"]),
        vm.Filter(id="tip_filter", column="tip", targets=["tips_table"]),
    ],  # (2)!
)

# ====== Reset controls ======
# TODO: Does not work as:
#  1. Button component does not support the `set_control` action yet.


ORIGINAL_CHECKLIST_VALUE = ["Asia", "Europe"]
ORIGINAL_DROPDOWN_VALUE = ["Afghanistan", "Albania"]


@capture("action")
def reset_filters():
    return ORIGINAL_CHECKLIST_VALUE, ORIGINAL_DROPDOWN_VALUE


page_7 = vm.Page(
    title="Reset Controls",
    components=[
        vm.Graph(figure=px.scatter(df_gapminder, x="gdpPercap", y="lifeExp", size="pop", color="continent")),
        vm.Button(
            icon="Reset Focus",
            text="",
            # actions=[
            #     set_control(control="p7_filter_1", value=ORIGINAL_CHECKLIST_VALUE),
            #     set_control(control="p7_filter_2", value=ORIGINAL_DROPDOWN_VALUE),
            # ],
            actions=vm.Action(function=reset_filters(), outputs=["p7_filter_1", "p7_filter_2"]),
        ),
    ],
    controls=[
        vm.Filter(id="p7_filter_1", column="continent", selector=vm.Checklist(value=ORIGINAL_CHECKLIST_VALUE)),
        vm.Filter(id="p7_filter_2", column="country", selector=vm.Dropdown(value=ORIGINAL_DROPDOWN_VALUE)),
    ],
)


# ====== Cascading controls ======
# TODO: Does not work as:
#  1. Form component does not support the `set_control` action yet.
#  2. Can't be used as and "value" and "options" have to be updated too. Should we recreate the selector?
#  3. Think about dynamic data here.
#  4. Think about persistence per cascading filter value. See first example here: https://dash.plotly.com/persistence


@capture("action")
def update_country_options_value(_trigger):
    continent = _trigger
    if continent:
        filtered_df = df_gapminder[df_gapminder["continent"].isin([continent])]
        options = [{"label": c, "value": c} for c in sorted(filtered_df["country"].unique())]
        value = [options[0]["value"]] if options else []
        return options, value
    return [], []


page_8 = vm.Page(
    title="Cascading Controls",
    components=[
        vm.Graph(
            figure=px.scatter(
                df_gapminder,
                x="gdpPercap",
                y="lifeExp",
                size="pop",
                color="continent",
                custom_data=["continent", "country"],
            )
        ),
    ],
    controls=[
        vm.Filter(
            column="continent",
            selector=vm.RadioItems(
                # set_control currently can't be added to the form component
                # actions=set_control(control="country_filter", value="value")
                actions=[
                    vm.Action(
                        function=update_country_options_value(),
                        outputs=["country_filter.options", "country_filter.value"],
                    )
                ]
            ),
        ),
        vm.Filter(id="country_filter", column="country", selector=vm.Checklist()),
    ],
)

# ====== Synced control values ======
# TODO: Does not work as:
#  1. Form component does not support the `set_control` action yet.
#  2. By setting set_control on the source filter.selector, the filter_action is overwritten.
#     Should we say that by attaching actions to the Filter, the actions are added on top of the filter action?
#     Otherwise, users should use pure form component. The problem here is that sometimes users maybe want to attach
#     The action before the filter_action. Does it mean we should make filter_action public so they can user it in the
#     way they want? What does vm.Filter mean? What does filter_action mean? We should clarify this for us and users.


@capture("action")
def sync_filter_values(_trigger):
    return _trigger


page_9 = vm.Page(
    title="Synced filter values",
    components=[
        vm.Container(
            controls=[
                vm.Filter(
                    column="species",
                    selector=vm.Checklist(
                        # actions=set_control(control="p8_filter_2", value="value")
                        actions=vm.Action(
                            function=sync_filter_values(),
                            outputs=["p9_filter_2"],
                        )
                    ),
                )
            ],
            components=[vm.Graph(figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"))],
        ),
        vm.Container(
            controls=[vm.Filter(id="p9_filter_2", column="species")],
            components=[vm.Graph(figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"))],
        ),
    ],
)

dashboard = vm.Dashboard(
    pages=[page_1, page_2, page_3, page_4, page_5, page_6, page_7, page_8, page_9],
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
                "Old AgGrid Filter interaction",
            ],
            "Advanced single page features": [
                "Reset Controls",
                "Cascading Controls",
                "Synced filter values",
            ],
        }
    ),
)

print(dashboard.model_dump())
# Vizro().build(dashboard).run()
