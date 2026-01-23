import e2e.vizro.constants as cnst

import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions import set_control
from vizro.models.types import capture
from vizro.tables import dash_ag_grid

iris = px.data.iris()

iris_unique_species = px.data.iris()
unique_species = iris_unique_species["species"].unique()
n_species = len(unique_species)
n_rows = len(iris_unique_species)
iris_unique_species["species"] = [unique_species[i % n_species] for i in range(n_rows)]

gapminder = px.data.gapminder()


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
            figure=dash_ag_grid(iris_unique_species),
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
