import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.figures import kpi_card  # (1)!

tips = px.data.tips()

page = vm.Page(
    title="KPI card",
    layout=vm.Flex(direction="row"),  # (2)!
    components=[
        vm.Figure(
            figure=kpi_card(
                data_frame=tips,
                value_column="tip",
                value_format="${value:.2f}",
                icon="Shopping Cart",
                title="Average Price",
            )
        )
    ],
    controls=[vm.Filter(column="day", selector=vm.RadioItems())],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
