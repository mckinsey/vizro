"""Dev app to try things out."""

import vizro.plotly.express as px
import vizro.models as vm
import vizro.actions as va

from vizro import Vizro
from vizro.models.types import capture
from vizro.tables import dash_ag_grid


df = px.data.iris()

page = vm.Page(
    title="Iris",
    components=[vm.AgGrid(figure=dash_ag_grid(df))],
)

dashboard = vm.Dashboard(pages=[page])
if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
