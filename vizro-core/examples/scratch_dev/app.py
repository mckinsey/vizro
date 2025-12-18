"""Dev app to try things out."""

import vizro.plotly.express as px
import vizro.models as vm
import vizro.actions as va

from vizro import Vizro
from vizro.models.types import capture
from vizro.tables import dash_ag_grid


df = px.data.iris()
df_6 = df.iloc[[0, 1, 50, 51, 100, 101]]


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
        ),
    ]


def _create_set_control_actions(prefix: str, value=None):
    return [
        va.set_control(control=f"{prefix}filter_1", value=value or "customdata[0]"),
        va.set_control(control=f"{prefix}filter_2", value=value or "customdata[0]"),
        va.set_control(control=f"{prefix}filter_3", value=value or "species"),
        va.set_control(control=f"{prefix}filter_4", value=value or "species"),
    ]


@capture("graph")
def bar_with_clickmode_event(data_frame, **kwargs):
    fig = px.bar(data_frame, **kwargs)
    fig.update_layout(clickmode="event")
    return fig


@capture("figure")
def text_as_figure(data_frame, text):
    return vm.Text(text=f"Selected countries: {str(text)}").build()


pre = "p1_"
page_1 = vm.Page(
    title="set_control via selectedData",
    layout=vm.Grid(grid=[[0], [0], [1]]),
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Bar, Scatter, Histogram",
                    layout=vm.Grid(grid=[[0, 1, 2]]),
                    components=[
                        vm.Graph(
                            figure=px.bar(
                                df,
                                x="sepal_width",
                                y="sepal_length",
                                color="species",
                                custom_data=["species"],
                            ),
                            actions=_create_set_control_actions(prefix=pre),
                        ),
                        vm.Graph(
                            figure=px.scatter(
                                df,
                                x="sepal_width",
                                y="sepal_length",
                                size="petal_length",
                                color="species",
                                custom_data=["species"],
                            ),
                            actions=_create_set_control_actions(prefix=pre),
                        ),
                        vm.Graph(
                            figure=px.histogram(df, x="species", color="sepal_length"),
                            actions=_create_set_control_actions(prefix=pre, value="x"),
                        ),
                    ],
                ),
                vm.Container(
                    title="Choropleth",
                    layout=vm.Grid(grid=[[0], [0], [0], [1]]),
                    components=[
                        vm.Graph(
                            id=f"{pre}choropleth",
                            figure=px.choropleth(
                                data_frame=px.data.gapminder().query("year==2007"),
                                locations="iso_alpha",
                                color="lifeExp",
                                hover_name="country",
                                custom_data=["country"],
                            ),
                            actions=va.set_control(control=f"{pre}parameter_1", value="country"),
                        ),
                        vm.Figure(
                            id="selected_countries_text",
                            figure=text_as_figure(px.data.gapminder(), text="Selected countries: None"),
                        ),
                    ],
                    controls=[
                        vm.Parameter(
                            id=f"{pre}parameter_1",
                            targets=["selected_countries_text.text"],
                            selector=vm.Dropdown(
                                options=px.data.gapminder().query("year==2007")["country"].unique().tolist()
                            ),
                            visible=False,
                        )
                    ],
                ),
            ]
        ),
        vm.AgGrid(id=f"{pre}table", figure=dash_ag_grid(px.data.iris())),
    ],
    controls=_create_filters(prefix=pre),
)

pre = "p2_"
page_2 = vm.Page(
    title="set_control via clickData",
    layout=vm.Grid(grid=[[0], [0], [1]]),
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Bar, Box, Violin",
                    layout=vm.Grid(grid=[[0, 1, 2]]),
                    components=[
                        vm.Graph(
                            title="Bar with explicitly clickmode='event' set",
                            figure=bar_with_clickmode_event(
                                df,
                                x="sepal_width",
                                y="sepal_length",
                                color="species",
                                custom_data=["species"],
                            ),
                            actions=_create_set_control_actions(prefix=pre),
                        ),
                        vm.Graph(
                            title="Box without selection enabled",
                            figure=px.box(df, x="species", y="sepal_length", color="species", custom_data=["species"]),
                            actions=_create_set_control_actions(prefix=pre),
                        ),
                        vm.Graph(
                            title="Violin without selection enabled",
                            figure=px.violin(
                                df, x="species", y="sepal_length", color="species", custom_data=["species"]
                            ),
                            actions=_create_set_control_actions(prefix=pre),
                        ),
                    ],
                ),
                vm.Container(
                    title="Area, Pie, Line, Funnel_Area",
                    layout=vm.Grid(grid=[[0, 1], [2, 3]]),
                    components=[
                        vm.Graph(
                            figure=px.area(
                                df,
                                x="sepal_width",
                                y="sepal_length",
                                color="species",
                                custom_data="species",
                            ),
                            actions=_create_set_control_actions(prefix=pre),
                        ),
                        vm.Graph(
                            figure=px.pie(df, names="species", values="sepal_length", custom_data=["species"]),
                            actions=_create_set_control_actions(prefix=pre),
                        ),
                        vm.Graph(
                            figure=px.line(
                                df,
                                x="sepal_width",
                                y="sepal_length",
                                color="species",
                                custom_data=["species"],
                            ),
                            actions=_create_set_control_actions(prefix=pre),
                        ),
                        vm.Graph(
                            figure=px.funnel_area(df, names="species", values="sepal_length", custom_data=["species"]),
                            actions=_create_set_control_actions(prefix=pre),
                        ),
                    ],
                ),
                vm.Container(
                    title="Density Heatmap, Line Polar, Treemap, Parallel Coordinates",
                    layout=vm.Grid(grid=[[0, 1], [2, 3]]),
                    components=[
                        vm.Graph(
                            title="IMPORTANT: Does not support custom_data.",
                            figure=px.density_heatmap(df, x="sepal_width", y="sepal_length"),
                            actions=_create_set_control_actions(prefix=pre),
                        ),
                        vm.Graph(
                            figure=px.line_polar(
                                df,
                                r="sepal_length",
                                theta="species",
                                color="species",
                                custom_data=["species"],
                            ),
                            actions=_create_set_control_actions(prefix=pre),
                        ),
                        vm.Graph(
                            figure=px.treemap(df, path=["species"], values="sepal_length", custom_data=["species"]),
                            actions=_create_set_control_actions(prefix=pre),
                        ),
                        vm.Graph(
                            title="IMPORTANT: Does not support custom_data nor clickData :D",
                            figure=px.parallel_coordinates(
                                df,
                                color="sepal_length",
                                dimensions=["sepal_width", "sepal_length", "petal_width", "petal_length"],
                            ),
                            actions=_create_set_control_actions(prefix=pre),
                        ),
                    ],
                ),
            ]
        ),
        vm.AgGrid(id=f"{pre}table", figure=dash_ag_grid(px.data.iris())),
    ],
    controls=_create_filters(prefix=pre),
)

pre = "p3_"
page_3 = vm.Page(
    title="set_control from ag-grid",
    components=[
        vm.AgGrid(
            figure=dash_ag_grid(df_6),
            actions=_create_set_control_actions(prefix=pre, value="species"),
        ),
        vm.AgGrid(id=f"{pre}table", figure=dash_ag_grid(px.data.iris())),
    ],
    controls=_create_filters(prefix=pre),
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
            ],
        ),
        vm.Button(
            text="Set []",
            actions=[
                va.set_control(control=f"{pre}filter_1", value=[]),
                va.set_control(control=f"{pre}filter_2", value=[]),
                va.set_control(control=f"{pre}filter_3", value=[]),
                va.set_control(control=f"{pre}filter_4", value=[]),
            ],
        ),
        vm.Card(
            text="Set 'versicolor'",
            actions=_create_set_control_actions(prefix=pre, value="versicolor"),
        ),
        vm.Card(
            text="""Set [['setosa', 'versicolor']]""",
            actions=_create_set_control_actions(prefix=pre, value=["setosa", "versicolor"]),
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
                    figure=px.bar(df, x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
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
            ],
        ),
        vm.Container(
            title="Set single-select",
            layout=vm.Flex(),
            components=[
                vm.Graph(
                    figure=px.bar(df, x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
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
            ],
        ),
    ],
)
page_6 = vm.Page(
    title="Drill-through target page",
    components=[
        vm.AgGrid(figure=dash_ag_grid(px.data.iris())),
    ],
    controls=[
        vm.Filter(id=f"{pre_target}filter_1", column="species", show_in_url=True),
        vm.Filter(
            id=f"{pre_target}filter_2",
            column="species",
            show_in_url=True,
            selector=vm.Dropdown(multi=False),
        ),
    ],
)

# Commenting out page_7 as filter_interaction is deprecated

# pre = "p7_"
# page_7 = vm.Page(
#     title="Old filter_interaction",
#     components=[
#         vm.Graph(
#             figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
#             actions=va.filter_interaction(targets=[f"{pre}table"]),
#         ),
#         vm.AgGrid(id=f"{pre}table", figure=dash_ag_grid(px.data.iris())),
#     ],
# )

pre = "p8_"
page_8 = vm.Page(
    title="Filtering graph/ag-grid that triggers set_control",
    layout=vm.Grid(grid=[[0, 1]]),
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Graph",
                    controls=[vm.Filter(column="species")],
                    components=[
                        vm.Graph(
                            id=f"{pre}graph_1",
                            title="Test whether the set_control is triggered when filter from container changes.",
                            figure=px.scatter(
                                df,
                                x="sepal_width",
                                y="sepal_length",
                                color="species",
                                custom_data=["species"],
                                color_discrete_map={
                                    "setosa": "#00b4ff",
                                    "versicolor": "#ff9222",
                                    "virginica": "#3949ab",
                                },
                            ),
                            actions=va.set_control(control=f"{pre}filter_1", value="customdata[0]"),
                        ),
                    ],
                ),
                vm.Container(
                    title="AgGrid",
                    controls=[vm.Filter(column="species")],
                    components=[
                        vm.AgGrid(
                            id=f"{pre}ag_grid_2",
                            figure=dash_ag_grid(df_6),
                            actions=va.set_control(control=f"{pre}filter_1", value="species"),
                        ),
                    ],
                ),
            ]
        ),
        vm.AgGrid(id=f"{pre}table", figure=dash_ag_grid(px.data.iris())),
    ],
    controls=[
        vm.Filter(
            id=f"{pre}filter_1",
            targets=[f"{pre}table"],
            column="species",
        )
    ],
)

pre = "p9_"
page_9 = vm.Page(
    title="Self-filtering graph",
    components=[
        vm.Graph(
            id=f"{pre}graph_1",
            figure=px.scatter(
                df,
                x="sepal_width",
                y="sepal_length",
                color="species",
                custom_data=["species"],
                color_discrete_map={"setosa": "#00b4ff", "versicolor": "#ff9222", "virginica": "#3949ab"},
            ),
            actions=va.set_control(control=f"{pre}filter_1", value="customdata[0]"),
        ),
    ],
    controls=[
        vm.Filter(
            id=f"{pre}filter_1",
            column="species",
        )
    ],
)


@capture("ag_grid")
def custom_dash_ag_grid(data_frame, **kwargs):
    grid = dash_ag_grid(data_frame, **kwargs)()
    return grid


pre = "p10_"
page_10 = vm.Page(
    title="AgGrid automatic checkboxes test",
    # layout=vm.Grid(grid=[[0], [0], [1]]),
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="dash_ag_grid",
                    layout=vm.Flex(direction="row"),
                    components=[
                        vm.AgGrid(
                            id=f"{pre}_ag_grid_1",
                            title="Standard AgGrid",
                            figure=dash_ag_grid(df_6),
                        ),
                        vm.AgGrid(
                            id=f"{pre}_ag_grid_2",
                            title="AgGrid with set_control",
                            figure=dash_ag_grid(df_6),
                            actions=va.set_control(control=f"{pre}filter_1", value="species"),
                        ),
                        vm.AgGrid(
                            id=f"{pre}_ag_grid_3",
                            title="AgGrid with set_control and explicit checkboxes=False config",
                            figure=dash_ag_grid(
                                df_6, dashGridOptions=dict(rowSelection=dict(checkboxes=False, headerCheckbox=False))
                            ),
                            actions=va.set_control(control=f"{pre}filter_1", value="species"),
                        ),
                    ],
                ),
                vm.Container(
                    title="Custom AgGrid figure functions",
                    layout=vm.Flex(direction="row"),
                    components=[
                        vm.AgGrid(id=f"{pre}_ag_grid_4", title="Custom AgGrid", figure=dash_ag_grid(df_6)),
                        vm.AgGrid(
                            id=f"{pre}_ag_grid_5",
                            title="Custom AgGrid with set_control",
                            figure=custom_dash_ag_grid(df_6),
                            actions=va.set_control(control=f"{pre}filter_1", value="species"),
                        ),
                        vm.AgGrid(
                            id=f"{pre}_ag_grid_6",
                            title="Custom AgGrid with set_control and explicit checkboxes=False config",
                            figure=custom_dash_ag_grid(
                                df_6, dashGridOptions=dict(rowSelection=dict(checkboxes=False, headerCheckbox=False))
                            ),
                            actions=va.set_control(control=f"{pre}filter_1", value="species"),
                        ),
                    ],
                ),
            ]
        ),
        vm.AgGrid(id=f"{pre}table", title="Control Target", figure=dash_ag_grid(px.data.iris())),
    ],
    controls=[vm.Filter(id=f"{pre}filter_1", column="species", targets=[f"{pre}table"])],
)

dashboard = vm.Dashboard(
    pages=[
        page_1,
        page_2,
        page_3,
        page_4,
        page_5,
        page_6,
        # Commenting out page_7 as filter_interaction is deprecated
        # page_7,
        page_8,
        page_9,
        page_10,
    ]
)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
