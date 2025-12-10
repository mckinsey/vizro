"""Dev app to try things out."""

import vizro.plotly.express as px
import vizro.models as vm
import vizro.actions as va

from vizro import Vizro
from vizro.models.types import capture
from vizro.tables import dash_ag_grid


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
                                px.data.iris(),
                                x="sepal_width",
                                y="sepal_length",
                                color="species",
                                custom_data=["species"],
                            ),
                            actions=_create_set_control_actions(prefix=pre),
                        ),
                        vm.Graph(
                            figure=px.scatter(
                                px.data.iris(),
                                x="sepal_width",
                                y="sepal_length",
                                size="petal_length",
                                color="species",
                                custom_data=["species"],
                            ),
                            actions=_create_set_control_actions(prefix=pre),
                        ),
                        vm.Graph(
                            figure=px.histogram(px.data.iris(), x="species", color="sepal_length"),
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
                                px.data.iris(),
                                x="sepal_width",
                                y="sepal_length",
                                color="species",
                                custom_data=["species"],
                            ),
                            actions=_create_set_control_actions(prefix=pre),
                        ),
                        vm.Graph(
                            title="Box without selection enabled",
                            figure=px.box(
                                px.data.iris(), x="species", y="sepal_length", color="species", custom_data=["species"]
                            ),
                            actions=_create_set_control_actions(prefix=pre),
                        ),
                        vm.Graph(
                            title="Violin without selection enabled",
                            figure=px.violin(
                                px.data.iris(), x="species", y="sepal_length", color="species", custom_data=["species"]
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
                                px.data.iris(),
                                x="sepal_width",
                                y="sepal_length",
                                color="species",
                                custom_data="species",
                            ),
                            actions=_create_set_control_actions(prefix=pre),
                        ),
                        vm.Graph(
                            figure=px.pie(
                                px.data.iris(), names="species", values="sepal_length", custom_data=["species"]
                            ),
                            actions=_create_set_control_actions(prefix=pre),
                        ),
                        vm.Graph(
                            figure=px.line(
                                px.data.iris(),
                                x="sepal_width",
                                y="sepal_length",
                                color="species",
                                custom_data=["species"],
                            ),
                            actions=_create_set_control_actions(prefix=pre),
                        ),
                        vm.Graph(
                            figure=px.funnel_area(
                                px.data.iris(), names="species", values="sepal_length", custom_data=["species"]
                            ),
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
                            figure=px.density_heatmap(px.data.iris(), x="sepal_width", y="sepal_length"),
                            actions=_create_set_control_actions(prefix=pre),
                        ),
                        vm.Graph(
                            figure=px.line_polar(
                                px.data.iris(),
                                r="sepal_length",
                                theta="species",
                                color="species",
                                custom_data=["species"],
                            ),
                            actions=_create_set_control_actions(prefix=pre),
                        ),
                        vm.Graph(
                            figure=px.treemap(
                                px.data.iris(), path=["species"], values="sepal_length", custom_data=["species"]
                            ),
                            actions=_create_set_control_actions(prefix=pre),
                        ),
                        vm.Graph(
                            title="IMPORTANT: Does not support custom_data nor clickData :D",
                            figure=px.parallel_coordinates(
                                px.data.iris(),
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
            figure=dash_ag_grid(px.data.iris().iloc[[0, 1, 50, 51, 100, 101]]),
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
                    figure=px.bar(
                        px.data.iris(), x="sepal_width", y="sepal_length", color="species", custom_data=["species"]
                    ),
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
                    figure=px.bar(
                        px.data.iris(), x="sepal_width", y="sepal_length", color="species", custom_data=["species"]
                    ),
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


pre = "p7_"
page_7 = vm.Page(
    title="Old filter_interaction",
    components=[
        vm.Graph(
            figure=px.scatter(
                px.data.iris(), x="sepal_width", y="sepal_length", color="species", custom_data=["species"]
            ),
            actions=va.filter_interaction(targets=[f"{pre}table"]),
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
            figure=px.scatter(
                px.data.iris(),
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


dashboard = vm.Dashboard(pages=[page_1, page_2, page_3, page_4, page_5, page_6, page_7, page_8])

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
