"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.figures import kpi_card
from vizro.models.types import capture
from vizro.tables import dash_ag_grid, dash_data_table

df = px.data.iris()

page = vm.Page(
    title="Test",
    components=[
        vm.Graph(figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species")),
    ],
    controls=[vm.Filter(column="species")],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
