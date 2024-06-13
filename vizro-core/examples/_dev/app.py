"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.figures import kpi_card

tips = px.data.tips

page = vm.Page(
    title="KPI Indicators",
    layout=vm.Layout(grid=[[0, -1, -1, -1]] + [[-1, -1, -1, -1]] * 4),
    components=[
        vm.Figure(
            figure=kpi_card(
                data_frame=tips,
                value_column="tip",
                value_format="${value:.2f}",
                icon="shopping_cart",
                title="KPI Card I",
            )
        )
    ],
    controls=[vm.Filter(column="day", selector=vm.RadioItems())],
)


dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
