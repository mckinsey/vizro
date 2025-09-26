import e2e.vizro.constants as cnst

import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions import set_control
from vizro.tables import dash_ag_grid

df = px.data.iris()


drill_through_filter_page_1 = vm.Page(
    title=cnst.SET_CONTROL_FILTER_DRILL_THROUGH_SOURCE,
    components=[
        vm.Graph(
            id=cnst.SCATTER_FILTER_DRILL_THROUGH_SOURCE_ID,
            figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
            actions=set_control(control="p2_filter_1", value="species"),
        )
    ],
)

drill_through_filter_page_2 = vm.Page(
    title=cnst.SET_CONTROL_FILTER_DRILL_THROUGH_TARGET,
    components=[
        vm.Graph(
            id=cnst.SCATTER_FILTER_DRILL_THROUGH_TARGET_ID,
            figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"),
        )
    ],
    controls=[
        vm.Filter(
            id="p2_filter_1",
            column="species",
            show_in_url=True,
            selector=vm.Checklist(id=cnst.CHECKLIST_FILTER_DRILL_THROUGH_ID),
        ),
    ],
)


drill_through_parameter_page_1 = vm.Page(
    title=cnst.SET_CONTROL_PARAMETER_DRILL_THROUGH_SOURCE,
    components=[
        vm.Graph(
            id=cnst.SCATTER_PARAMETER_DRILL_THROUGH_SOURCE_ID,
            figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
            actions=set_control(control="p2_parameter_1", value="species"),
        )
    ],
)

drill_through_parameter_page_2 = vm.Page(
    title=cnst.SET_CONTROL_PARAMETER_DRILL_THROUGH_TARGET,
    components=[
        vm.Graph(
            id=cnst.SCATTER_PARAMETER_DRILL_THROUGH_TARGET_ID,
            figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"),
        )
    ],
    controls=[
        vm.Parameter(
            id="p2_parameter_1",
            targets=[f"{cnst.SCATTER_PARAMETER_DRILL_THROUGH_TARGET_ID}.title"],
            selector=vm.RadioItems(
                id=cnst.RADIOITEMS_PARAMETER_DRILL_THROUGH_ID,
                options=["setosa", "versicolor", "virginica"],
                value="virginica",
            ),
            show_in_url=True,
        ),
    ],
)

drill_through_filter_ag_grid_page_1 = vm.Page(
    title=cnst.SET_CONTROL_FILTER_DRILL_THROUGH_AG_GRID_SOURCE,
    components=[
        vm.AgGrid(
            id=cnst.AG_GRID_DRILL_THROUGH_ID,
            figure=dash_ag_grid(df),
            actions=set_control(control="p5_filter_1", value="species"),
        ),
    ],
    controls=[
        vm.Filter(column="species", selector=vm.Dropdown(value="virginica")),
    ],
)

drill_through_filter_ag_grid_page_2 = vm.Page(
    title=cnst.SET_CONTROL_FILTER_DRILL_THROUGH_AG_GRID_TARGET,
    components=[
        vm.Graph(
            id=cnst.SCATTER_SECOND_FILTER_DRILL_THROUGH_TARGET_ID,
            figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"),
        )
    ],
    controls=[
        vm.Filter(
            id="p5_filter_1",
            column="species",
            show_in_url=True,
            selector=vm.RadioItems(id=cnst.RADIOITEMS_FILTER_DRILL_THROUGH_ID),
        ),
    ],
)
