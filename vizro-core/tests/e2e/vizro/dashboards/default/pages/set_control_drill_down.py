import e2e.vizro.constants as cnst

import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions import set_control
from vizro.models.types import capture

df = px.data.iris()


@capture("graph")
def graph_with_dynamic_title(data_frame, title="ALL", **kwargs):
    return px.scatter(data_frame, title=f"Graph shows `{title}` species.", **kwargs)


drill_down_graph_page = vm.Page(
    title=cnst.SET_CONTROL_DRILL_DOWN_GRAPH_PAGE,
    components=[
        vm.Graph(
            id=cnst.SCATTER_DRILL_DOWN_GRAPH_ID,
            figure=graph_with_dynamic_title(
                data_frame=df, x="sepal_width", y="sepal_length", color="species", custom_data=["species"]
            ),
            actions=[
                set_control(control="p3-filter-1", value="species"),
                set_control(control="p3-parameter-1", value="species"),
            ],
        )
    ],
    controls=[
        vm.Filter(id="p3-filter-1", column="species"),
        vm.Parameter(
            id="p3-parameter-1",
            targets=[f"{cnst.SCATTER_DRILL_DOWN_GRAPH_ID}.title"],
            selector=vm.Dropdown(options=["setosa", "versicolor", "virginica"]),
        ),
    ],
)
