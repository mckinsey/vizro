import e2e.vizro.constants as cnst

import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions import export_data

iris = px.data.iris()

filters_page = vm.Page(
    title=cnst.FILTERS_PAGE,
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    id=cnst.FILTERS_TAB_CONTAINER,
                    title=cnst.FILTERS_TAB_CONTAINER,
                    components=[
                        vm.Container(
                            id=cnst.FILTERS_COMPONENTS_CONTAINER,
                            title=cnst.FILTERS_COMPONENTS_CONTAINER,
                            layout=vm.Grid(grid=[[0, 1], [0, 1], [0, 2]]),
                            components=[
                                vm.Graph(
                                    id=cnst.SCATTER_GRAPH_ID,
                                    figure=px.scatter(
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
                                ),
                                vm.Button(
                                    text="Export data",
                                    actions=[
                                        vm.Action(
                                            function=export_data(
                                                targets=[cnst.SCATTER_GRAPH_ID],
                                                file_format="csv",
                                            )
                                        ),
                                        vm.Action(
                                            function=export_data(
                                                targets=[cnst.SCATTER_GRAPH_ID],
                                                file_format="xlsx",
                                            )
                                        ),
                                    ],
                                ),
                            ],
                        )
                    ],
                )
            ]
        ),
        vm.Graph(
            id=cnst.BOX_GRAPH_ID,
            figure=px.box(
                iris,
                x="sepal_length",
                y="petal_width",
                color="sepal_width",
            ),
            extra={"config": {"displayModeBar": False}},
        ),
    ],
    controls=[
        vm.Filter(
            column="species",
            targets=[cnst.SCATTER_GRAPH_ID, cnst.BOX_GRAPH_ID],
            selector=vm.Dropdown(id=cnst.DROPDOWN_FILTER_FILTERS_PAGE),
        ),
        vm.Filter(
            column="species",
            targets=[cnst.SCATTER_GRAPH_ID, cnst.BOX_GRAPH_ID],
            selector=vm.RadioItems(
                id=cnst.RADIO_ITEMS_FILTER_FILTERS_PAGE, options=["setosa", "versicolor", "virginica"]
            ),
        ),
        vm.Filter(
            column="species",
            targets=[cnst.SCATTER_GRAPH_ID],
            selector=vm.Checklist(
                id=cnst.CHECK_LIST_FILTER_FILTERS_PAGE, options=["setosa", "versicolor", "virginica"]
            ),
        ),
        vm.Filter(
            column="petal_width",
            targets=[cnst.SCATTER_GRAPH_ID],
            selector=vm.Slider(id=cnst.SLIDER_FILTER_FILTERS_PAGE, step=0.5),
        ),
        vm.Filter(
            column="sepal_length",
            targets=[cnst.SCATTER_GRAPH_ID, cnst.BOX_GRAPH_ID],
            selector=vm.RangeSlider(id=cnst.RANGE_SLIDER_FILTER_FILTERS_PAGE, step=1.0),
        ),
    ],
)
