import e2e.vizro.constants as cnst
import pandas as pd

import vizro.models as vm
import vizro.plotly.express as px

iris = px.data.iris()
iris["date_column"] = pd.date_range(start=pd.to_datetime("2024-01-01"), periods=len(iris), freq="D")
gapminder = px.data.gapminder()

filters_inside_containers_page = vm.Page(
    title=cnst.FILTERS_INSIDE_CONTAINERS_PAGE,
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="container",
                    variant="filled",
                    components=[
                        vm.Container(
                            layout=vm.Grid(grid=[[0, 1]]),
                            title="container",
                            variant="filled",
                            components=[
                                vm.Graph(
                                    id=cnst.SCATTER_INSIDE_CONTAINER,
                                    figure=px.scatter(
                                        iris,
                                        x="sepal_length",
                                        y="petal_width",
                                        color="sepal_width",
                                    ),
                                ),
                                vm.Graph(
                                    id="scatter2",
                                    figure=px.scatter(
                                        gapminder,
                                        x="year",
                                        y="gdpPercap",
                                    ),
                                ),
                            ],
                        )
                    ],
                    controls=[
                        vm.Filter(
                            column="species",
                            selector=vm.Dropdown(id=cnst.DROPDOWN_INSIDE_CONTAINERS),
                        ),
                        vm.Filter(
                            column="species",
                            selector=vm.RadioItems(
                                id=cnst.RADIO_ITEMS_INSIDE_CONTAINERS,
                                options=["setosa", "versicolor", "virginica"],
                                extra={"inline": True},
                            ),
                        ),
                        vm.Filter(
                            column="species",
                            selector=vm.Checklist(
                                id=cnst.CHECK_LIST_INSIDE_CONTAINERS,
                                options=["setosa", "versicolor", "virginica"],
                                extra={"inline": True},
                            ),
                        ),
                        vm.Filter(
                            column="petal_width",
                            selector=vm.Slider(id=cnst.SLIDER_INSIDE_CONTAINERS, step=0.5),
                        ),
                        vm.Filter(
                            column="sepal_length",
                            selector=vm.RangeSlider(id=cnst.RANGE_SLIDER_INSIDE_CONTAINERS, step=1.0),
                        ),
                        vm.Filter(
                            column="date_column",
                            selector=vm.DatePicker(
                                id=cnst.RANGE_DATEPICKER_INSIDE_CONTAINERS,
                                title="Custom styled date picker",
                                range=True,
                                extra={
                                    "size": "lg",
                                    "valueFormat": "YYYY/MM/DD",
                                    "placeholder": "Select a date",
                                },
                            ),
                        ),
                    ],
                ),
            ]
        ),
    ],
)
