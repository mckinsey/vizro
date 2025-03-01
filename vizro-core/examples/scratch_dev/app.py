import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid
from vizro.models.types import capture
from vizro.figures import kpi_card

tips = px.data.tips()

first_page = vm.Page(
    title="Data",
    components=[
        vm.AgGrid(
            figure=dash_ag_grid(tips),
            footer="""**Data Source:** Bryant, P. G. and Smith, M (1995)
            Practical Data Analysis: Case Studies in Business Statistics.
            Homewood, IL: Richard D. Irwin Publishing.""",
        ),
    ],
)

second_page = vm.Page(
    title="Summary",
    components=[
        vm.Figure(
            figure=kpi_card(
                data_frame=tips,
                value_column="total_bill",
                agg_func="mean",
                value_format="${value:.2f}",
                title="Average Bill",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=tips, value_column="tip", agg_func="mean", value_format="${value:.2f}", title="Average Tips"
            )
        ),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Total Bill ($)",
                    components=[
                        vm.Graph(figure=px.histogram(tips, x="total_bill")),
                    ],
                ),
                vm.Container(
                    title="Total Tips ($)",
                    components=[
                        vm.Graph(figure=px.histogram(tips, x="tip")),
                    ],
                ),
            ],
        ),
    ],
)

dashboard = vm.Dashboard(pages=[first_page, second_page])
Vizro().build(dashboard).run()
