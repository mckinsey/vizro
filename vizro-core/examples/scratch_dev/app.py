import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid

iris = px.data.iris()

overview_page = vm.Page(
    title="Overview",
    components=[
        vm.AgGrid(id="overview_table", figure=dash_ag_grid(iris)),
    ],
    controls=[
        vm.Filter(
            column="species",
            targets=["overview_table", "detail_species"],  # (1)!
            selector=vm.Dropdown(title="Species"),
        ),
    ],
)

detail_page = vm.Page(
    title="Detail",
    components=[
        vm.Graph(id="detail_graph", figure=px.scatter(iris, x="petal_width", y="petal_length", color="species")),
    ],
    controls=[
        vm.Filter(id="detail_species", column="species", targets=["detail_graph"]),  # (2)!
    ],
)

dashboard = vm.Dashboard(pages=[overview_page, detail_page])
Vizro().build(dashboard).run()