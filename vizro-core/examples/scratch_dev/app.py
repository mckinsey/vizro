# Vizro is an open-source toolkit for creating modular data visualization applications.
# check out https://github.com/mckinsey/vizro for more info about Vizro
# and checkout https://vizro.readthedocs.io/en/stable/ for documentation.
import pandas as pd
import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
from vizro.actions import filter_interaction, export_data
from vizro.tables import dash_data_table

tips = px.data.tips()
gapminder = px.data.gapminder()
iris = px.data.iris()
iris2 = px.data.iris()
iris2["date_column"] = pd.date_range(start=pd.to_datetime("2024-01-01"), periods=len(iris), freq="D")

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
            selector=vm.RadioItems(id="RADIOITEM_INTER_PARAM", options=["red", "blue"], value="blue"),
        ),
    ],
)


page2 = vm.Page(
    title="FILTERS_PAGE",
    components=[
        vm.Tabs(
            tabs=[
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
            ]
        ),
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
                        iris2,
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
dashboard = vm.Dashboard(
    title="Vizro dashboard for integration testing",
    pages=[page, page1, page2, page3],
)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
