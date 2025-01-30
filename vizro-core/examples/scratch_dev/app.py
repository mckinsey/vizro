"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.figures import kpi_card

tips = px.data.tips

# Create a layout with five rows and four columns. The KPI card is positioned in the first cell, while the remaining cells are empty.
page = vm.Page(
    title="KPI card",
    layout=vm.Layout(grid=[[0, 0, -1, -1]] + [[-1, -1, -1, -1]] * 2),
    components=[
        vm.Figure(
            figure=kpi_card(  # For more information, refer to the API reference for kpi_card
                data_frame=tips,
                value_column="tip",
                value_format="${value:.2f}",
                icon="folder_check",
                title="KPI card I",
            )
        )
    ],
    controls=[vm.Filter(column="day", selector=vm.RadioItems())],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
