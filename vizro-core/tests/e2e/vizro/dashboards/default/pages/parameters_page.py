import e2e.vizro.constants as cnst

import vizro.models as vm
import vizro.plotly.express as px

iris = px.data.iris()

parameters_page = vm.Page(
    title=cnst.PARAMETERS_PAGE,
    path=cnst.PARAMETERS_PAGE_PATH,
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    id=cnst.PARAMETERS_TAB_CONTAINER,
                    title=cnst.PARAMETERS_TAB_CONTAINER,
                    components=[
                        vm.Tabs(
                            id=cnst.PARAMETERS_SUB_TAB_ID,
                            tabs=[
                                vm.Container(
                                    id=cnst.PARAMETERS_SUB_TAB_CONTAINER_ONE,
                                    title=cnst.PARAMETERS_SUB_TAB_CONTAINER_ONE,
                                    components=[
                                        vm.Graph(
                                            id=cnst.BAR_GRAPH_ID,
                                            figure=px.bar(
                                                iris,
                                                x="sepal_length",
                                                y="petal_width",
                                                color="species",
                                                color_discrete_map={
                                                    "setosa": "black",
                                                    "versicolor": "pink",
                                                },
                                            ),
                                        )
                                    ],
                                ),
                                vm.Container(
                                    id=cnst.PARAMETERS_SUB_TAB_CONTAINER_TWO,
                                    title=cnst.PARAMETERS_SUB_TAB_CONTAINER_TWO,
                                    components=[
                                        vm.Graph(
                                            id=cnst.HISTOGRAM_GRAPH_ID,
                                            figure=px.histogram(
                                                iris,
                                                x="sepal_length",
                                                y="petal_width",
                                                color="species",
                                                color_discrete_map={
                                                    "setosa": "black",
                                                    "versicolor": "pink",
                                                },
                                            ),
                                        ),
                                    ],
                                ),
                            ],
                        )
                    ],
                )
            ]
        ),
        vm.Container(
            id=cnst.PARAMETERS_CONTAINER,
            title=cnst.PARAMETERS_CONTAINER,
            components=[
                vm.Graph(
                    id=cnst.BAR_GRAPH_ID_CONTAINER,
                    figure=px.bar(
                        iris,
                        x="sepal_length",
                        y="petal_width",
                        color="species",
                        color_discrete_map={
                            "setosa": "black",
                            "versicolor": "pink",
                        },
                    ),
                ),
            ],
        ),
    ],
    controls=[
        vm.Parameter(
            targets=[f"{cnst.BAR_GRAPH_ID}.color_discrete_map.virginica"],
            selector=vm.Dropdown(
                id=cnst.DROPDOWN_PARAMETERS_TWO, options=["NONE", "red", "blue"], multi=False, value="blue"
            ),
        ),
        vm.Parameter(
            targets=[f"{cnst.HISTOGRAM_GRAPH_ID}.color_discrete_map.setosa"],
            selector=vm.Dropdown(
                id=cnst.DROPDOWN_PARAMETERS_ONE, options=["NONE", "red", "blue"], multi=False, value="blue"
            ),
        ),
        vm.Parameter(
            targets=[f"{cnst.BAR_GRAPH_ID}.title", f"{cnst.HISTOGRAM_GRAPH_ID}.title"],
            selector=vm.RadioItems(id=cnst.RADIO_ITEMS_PARAMETERS_ONE, options=["red", "blue"], value="blue"),
        ),
        vm.Parameter(
            targets=[f"{cnst.BAR_GRAPH_ID}.y"],
            selector=vm.RadioItems(
                id=cnst.RADIO_ITEMS_PARAMETERS_TWO, options=["petal_width", "petal_length"], value="petal_width"
            ),
        ),
        vm.Parameter(
            targets=[f"{cnst.BAR_GRAPH_ID}.opacity"],
            selector=vm.Slider(id=cnst.SLIDER_PARAMETERS, min=0, max=1, value=0.2, step=0.2, title="Bubble opacity"),
        ),
        vm.Parameter(
            targets=[f"{cnst.HISTOGRAM_GRAPH_ID}.range_x"],
            selector=vm.RangeSlider(id=cnst.RANGE_SLIDER_PARAMETERS, min=4, max=8, step=1.0, title="Range X Histogram"),
        ),
    ],
)
