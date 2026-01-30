import e2e.vizro.constants as cnst
import numpy as np

import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions import set_control
from vizro.models.types import capture
from vizro.tables import dash_ag_grid

iris = px.data.iris()
unique_species = iris["species"].unique()
iris_species_cycle = iris.copy()
iris_species_cycle["species"] = np.resize(unique_species, len(iris_species_cycle))


@capture("graph")
def scatter_with_clickmode_event(data_frame, **kwargs):
    fig = px.scatter(data_frame, **kwargs)
    fig.update_layout(clickmode="event")
    return fig


cross_filter_multi_select_page = vm.Page(
    title=cnst.SET_CONTROL_MULTI_SELECT_PAGE,
    layout=vm.Grid(grid=[[0, 3], [1, 3], [2, 3]]),
    components=[
        vm.Graph(
            id=cnst.SCATTER_SET_CONTROL_EVENT_SELECT,
            figure=px.scatter(
                iris,
                x="sepal_length",
                y="petal_width",
                color="species",
                custom_data=["species"],
            ),
            actions=[
                set_control(control="chl_filter", value="species"),
                set_control(control="ri_filter", value="species"),
            ],
        ),
        vm.Graph(
            id=cnst.SCATTER_SET_CONTROL_EVENT,
            figure=scatter_with_clickmode_event(
                iris,
                x="sepal_length",
                y="petal_width",
                color="species",
                custom_data=["species"],
            ),
            actions=[
                set_control(control="chl_filter", value="species"),
                set_control(control="ri_filter", value="species"),
            ],
        ),
        vm.AgGrid(
            id=cnst.TABLE_SET_CONTROL_MULTI_SELECT,
            figure=dash_ag_grid(iris_species_cycle),
            actions=[
                set_control(control="chl_filter", value="species"),
                set_control(control="ri_filter", value="species"),
            ],
        ),
        vm.Graph(
            id=cnst.BOX_SET_CONTROL_TARGET_MULTI_SELECT,
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
            id="chl_filter",
            column="species",
            targets=[cnst.BOX_SET_CONTROL_TARGET_MULTI_SELECT],
            selector=vm.Checklist(id=cnst.CHECKLIST_SET_CONTROL_MULTI_SELECT_FILTER),
        ),
        vm.Filter(
            id="ri_filter",
            column="species",
            targets=[cnst.BOX_SET_CONTROL_TARGET_MULTI_SELECT],
            selector=vm.RadioItems(id=cnst.RADIOITEMS_SET_CONTROL_MULTI_SELECT_FILTER),
        ),
    ],
)


button_card_trigger_set_control = vm.Page(
    title=cnst.SET_CONTROL_BUTTON_CARD,
    components=[
        vm.Button(
            id=cnst.SET_CONTROL_BUTTON_NONE,
            actions=[
                set_control(control="chl_bc_filter", value=None),
                set_control(control="ri_bc_filter", value=None),
            ],
        ),
        vm.Button(
            id=cnst.SET_CONTROL_BUTTON_EMPTY_LIST,
            actions=[
                set_control(control="chl_bc_filter", value=[]),
                set_control(control="ri_bc_filter", value=[]),
            ],
        ),
        vm.Card(
            id=cnst.SET_CONTROL_CARD_SINGLE_VALUE,
            text="Set to 'virginica'",
            actions=[
                set_control(control="chl_bc_filter", value=["virginica"]),
                set_control(control="ri_bc_filter", value=["virginica"]),
            ],
        ),
        vm.Card(
            id=cnst.SET_CONTROL_CARD_MULTI_VALUE,
            text="Set to 'virginica' and 'versicolor'",
            actions=[
                set_control(control="chl_bc_filter", value=["virginica", "versicolor"]),
                set_control(control="ri_bc_filter", value=["virginica", "versicolor"]),
            ],
        ),
        vm.AgGrid(
            id=cnst.TABLE_SET_CONTROL_BUTTON_CARD,
            figure=dash_ag_grid(iris_species_cycle),
        ),
    ],
    controls=[
        vm.Filter(
            id="chl_bc_filter",
            column="species",
            targets=[cnst.TABLE_SET_CONTROL_BUTTON_CARD],
            selector=vm.Checklist(id=cnst.CHECKLIST_SET_CONTROL_BUTTON_CARD),
        ),
        vm.Filter(
            id="ri_bc_filter",
            column="species",
            targets=[cnst.TABLE_SET_CONTROL_BUTTON_CARD],
            selector=vm.RadioItems(id=cnst.RADIOITEMS_SET_CONTROL_BUTTON_CARD),
        ),
    ],
)


filtered_graph_aggrid_trigger_set_control = vm.Page(
    title=cnst.FILTERED_GRAPH_AGGRID_TRIGGER_SET_CONTROL_PAGE,
    layout=vm.Grid(grid=[[0, 1]]),
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Graph",
                    controls=[
                        vm.Filter(column="species", selector=vm.Checklist(id=cnst.CHECKLIST_FT_GRAPH_SET_CONTROL))
                    ],
                    components=[
                        vm.Graph(
                            id=cnst.FILTERED_SCATTER_TRIGGER_SET_CONTROL_ID,
                            figure=px.scatter(
                                iris,
                                x="sepal_width",
                                y="sepal_length",
                                color="species",
                                custom_data=["species"],
                            ),
                            actions=set_control(control="chl_ft_filter", value="species"),
                        ),
                    ],
                ),
                vm.Container(
                    title="AgGrid",
                    controls=[
                        vm.Filter(column="species", selector=vm.Checklist(id=cnst.CHECKLIST_FT_AGGRID_SET_CONTROL))
                    ],
                    components=[
                        vm.AgGrid(
                            id=cnst.FILTERED_AGGRID_TRIGGER_SET_CONTROL_ID,
                            figure=dash_ag_grid(iris_species_cycle),
                            actions=set_control(control="chl_ft_filter", value="species"),
                        ),
                    ],
                ),
            ]
        ),
        vm.AgGrid(id=cnst.TARGETED_AGGRID_FROM_FILTERED_GRAPH, figure=dash_ag_grid(iris)),
    ],
    controls=[
        vm.Filter(
            id="chl_ft_filter",
            column="species",
            targets=[cnst.TARGETED_AGGRID_FROM_FILTERED_GRAPH],
            selector=vm.Checklist(id=cnst.CHECKLIST_FILTERED_GRAPH_TARGET_AGGRID_SET_CONTROL),
        ),
    ],
)


self_filter_set_control_page = vm.Page(
    title=cnst.SELF_FILTER_SET_CONTROL_PAGE,
    components=[
        vm.Graph(
            id=cnst.SCATTER_SET_CONTROL_SELF_FILTER,
            figure=px.scatter(
                iris,
                x="sepal_length",
                y="petal_width",
                color="species",
                custom_data=["species"],
            ),
            actions=[
                set_control(control="chl_self_filter", value="species"),
            ],
        ),
    ],
    controls=[
        vm.Filter(
            id="chl_self_filter",
            column="species",
            selector=vm.Checklist(id=cnst.CHECKLIST_SET_CONTROL_SELF_FILTER),
        ),
    ],
)
