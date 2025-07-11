# Vizro is an open-source toolkit for creating modular data visualization applications.
# check out https://github.com/mckinsey/vizro for more info about Vizro
# and checkout https://vizro.readthedocs.io/en/stable/ for documentation.
import pandas as pd
import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
from vizro.actions import filter_interaction, export_data
from vizro.tables import dash_ag_grid, dash_data_table

tips = px.data.tips()
gapminder = px.data.gapminder()
iris = px.data.iris()
iris["date_column"] = pd.date_range(
    start=pd.to_datetime("2024-01-01"), periods=len(iris), freq="D"
)

page = vm.Page(
    title="TABLE_INTERACTIONS_PAGE",
    components=[
        vm.Container(
            title="container one",
            # layout=vm.Flex(direction="column"),
            components=[
                vm.Table(
                    id="TABLE_INTERACTIONS_ID",
                    title="Table Country",
                    figure=dash_data_table(
                        id="dash_data_table_country",
                        data_frame=gapminder,
                    ),
                    actions=[
                        vm.Action(
                            function=filter_interaction(
                                targets=[
                                    "LINE_INTERACTIONS_ID",
                                ]
                            )
                        )
                    ],
                ),
            ],
        ),
        vm.Container(
            title="container two",
            components=[
                vm.Graph(
                    id="LINE_INTERACTIONS_ID",
                    figure=px.line(
                        gapminder,
                        title="Line Country",
                        x="year",
                        y="gdpPercap",
                        markers=True,
                    ),
                ),
            ],
        ),
    ],
    controls=[
        vm.Filter(
            column="year",
            targets=["TABLE_INTERACTIONS_ID"],
            selector=vm.Dropdown(value=2007),
        ),
        vm.Filter(
            column="continent",
            targets=["TABLE_INTERACTIONS_ID"],
            selector=vm.RadioItems(options=["Europe", "Africa", "Americas"]),
        ),
    ],
)


page1 = vm.Page(
    title="FILTER_INTERACTIONS_PAGE",
    layout=vm.Grid(grid=[[0], [2], [1]]),
    components=[
        vm.Graph(
            id="SCATTER_INTERACTIONS_ID",
            figure=px.scatter(
                iris,
                x="sepal_length",
                y="petal_width",
                color="species",
                custom_data=["species"],
            ),
            actions=[
                vm.Action(function=filter_interaction(targets=["BOX_INTERACTIONS_ID"])),
            ],
        ),
        vm.Card(id="CARD_INTERACTIONS_ID", text="### No data clicked."),
        vm.Graph(
            id="BOX_INTERACTIONS_ID",
            figure=px.box(
                iris,
                x="sepal_length",
                y="petal_width",
                color="species",
            ),
        ),
    ],
    controls=[
        vm.Filter(
            column="species",
            targets=["BOX_INTERACTIONS_ID"],
            selector=vm.Dropdown(id="DROPDOWN_INTER_FILTER"),
        ),
        vm.Parameter(
            targets=["BOX_INTERACTIONS_ID.title"],
            selector=vm.RadioItems(
                id="RADIOITEM_INTER_PARAM", options=["red", "blue"], value="blue"
            ),
        ),
    ],
)


page2 = vm.Page(
    title="FILTERS_PAGE",
    components=[
        # vm.Tabs(
        #     tabs=[
        vm.Container(
            id="FILTERS_TAB_CONTAINER",
            title="FILTERS_TAB_CONTAINER",
            components=[
                vm.Container(
                    id="FILTERS_COMPONENTS_CONTAINER",
                    title="FILTERS_COMPONENTS_CONTAINER",
                    layout=vm.Grid(grid=[[0, 1], [0, 1], [0, 2]]),
                    components=[
                        vm.Graph(
                            id="SCATTER_GRAPH_ID",
                            figure=px.scatter(
                                iris,
                                x="sepal_length",
                                y="petal_width",
                                color="sepal_width",
                                height=450,
                            ),
                        ),
                        vm.Graph(
                            title="Where do we get more tips?",
                            figure=px.bar(tips, y="tip", x="day"),
                        ),
                        vm.Graph(
                            id="BOX_GRAPH_ID_2",
                            figure=px.box(
                                iris,
                                x="sepal_length",
                                y="petal_width",
                                color="sepal_width",
                            ),
                        ),
                    ],
                )
            ],
        ),
        #     ]
        # ),
        vm.Graph(
            id="BOX_GRAPH_ID",
            figure=px.box(
                iris,
                x="sepal_length",
                y="petal_width",
                color="sepal_width",
            ),
        ),
    ],
    controls=[
        vm.Filter(
            column="species",
            targets=["SCATTER_GRAPH_ID", "BOX_GRAPH_ID"],
            selector=vm.Dropdown(id="DROPDOWN_FILTER_FILTERS_PAGE"),
        ),
        vm.Filter(
            column="species",
            targets=["SCATTER_GRAPH_ID", "BOX_GRAPH_ID"],
            selector=vm.RadioItems(
                id="RADIO_ITEMS_FILTER_FILTERS_PAGE",
                options=["setosa", "versicolor", "virginica"],
            ),
        ),
        vm.Filter(
            column="species",
            targets=["SCATTER_GRAPH_ID"],
            selector=vm.Checklist(
                id="CHECK_LIST_FILTER_FILTERS_PAGE",
                options=["setosa", "versicolor", "virginica"],
            ),
        ),
        vm.Filter(
            column="petal_width",
            targets=["SCATTER_GRAPH_ID"],
            selector=vm.Slider(id="SLIDER_FILTER_FILTERS_PAGE", step=0.5),
        ),
        vm.Filter(
            column="sepal_length",
            targets=["SCATTER_GRAPH_ID", "BOX_GRAPH_ID"],
            selector=vm.RangeSlider(id="RANGE_SLIDER_FILTER_FILTERS_PAGE", step=1.0),
        ),
    ],
)


page3 = vm.Page(
    title="EXTRAS_PAGE",
    components=[
        vm.Container(
            extra={
                "class_name": "bg-container",
                "fluid": False,
                "style": {"height": "900px"},
            },
            components=[
                vm.Graph(
                    figure=px.line(
                        iris,
                        x="sepal_length",
                        y="petal_width",
                        color="sepal_width",
                    ),
                ),
                vm.Card(
                    text="""
    ![icon-top](assets/images/icons/content/features.svg)

    Leads to the home page on click.
    """,
                    href="/",
                    extra={"style": {"backgroundColor": "#377a6b"}},
                ),
                vm.Button(
                    text="Export data",
                    extra={"color": "success", "outline": True},
                    actions=[
                        vm.Action(
                            function=export_data(
                                file_format="csv",
                            )
                        ),
                    ],
                ),
            ],
        ),
    ],
    controls=[
        vm.Filter(
            column="species",
            selector=vm.Dropdown(
                extra={
                    "clearable": True,
                    "placeholder": "Select an option...",
                    "style": {"width": "150px"},
                },
            ),
        ),
        vm.Filter(
            column="species",
            selector=vm.RadioItems(
                description="RADIOITEMS_TOOLTIP_TEXT",
                options=["setosa", "versicolor", "virginica"],
                extra={"inline": True},
            ),
        ),
        vm.Filter(
            column="species",
            selector=vm.Checklist(
                options=["setosa", "versicolor", "virginica"],
                extra={"switch": True, "inline": True},
            ),
        ),
        vm.Filter(
            column="petal_width",
            selector=vm.Slider(
                step=0.5,
                extra={"tooltip": {"placement": "bottom", "always_visible": True}},
            ),
        ),
        vm.Filter(
            column="sepal_length",
            selector=vm.RangeSlider(
                step=1.0,
                extra={
                    "tooltip": {"placement": "bottom", "always_visible": True},
                    "pushable": 20,
                },
            ),
        ),
        vm.Filter(
            column="date_column",
            selector=vm.DatePicker(
                title="Custom styled date picker",
                range=False,
                extra={
                    "size": "lg",
                    "valueFormat": "YYYY/MM/DD",
                    "placeholder": "Select a date",
                },
            ),
        ),
    ],
)


# page11 = vm.Page(
#     title="Flex - default - aggrid",
#     layout=vm.Flex(),
#     components=[vm.AgGrid(figure=dash_ag_grid(tips)) for i in range(3)],
# )


# page12 = vm.Page(
#     title="Flex - gap - aggrid",
#     layout=vm.Grid(grid=[[0]]),
#     components=[vm.AgGrid(figure=dash_ag_grid(tips))],
# )

# page13 = vm.Page(
#     title="Flex - row - aggrid",
#     layout=vm.Flex(direction="row"),
#     components=[vm.AgGrid(figure=dash_ag_grid(tips)) for i in range(3)],
# )

# page14 = vm.Page(
#     title="Flex - default - table",
#     layout=vm.Flex(),
#     components=[vm.Table(figure=dash_data_table(tips)) for i in range(3)],
# )


# page15 = vm.Page(
#     title="Flex - gap - table",
#     layout=vm.Flex(gap="40px"),
#     components=[vm.Table(figure=dash_data_table(tips)) for i in range(3)],
# )

# page16 = vm.Page(
#     title="Flex - row - table",
#     layout=vm.Flex(direction="row"),
#     components=[vm.Table(figure=dash_data_table(tips)) for i in range(3)],
# )

dashboard = vm.Dashboard(
    title="Vizro dashboard for integration testing",
    pages=[page, page1, page2, page3],
)
Vizro().build(dashboard).run()
