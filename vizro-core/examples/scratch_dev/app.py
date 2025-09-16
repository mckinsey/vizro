import vizro.actions as va
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid

tips = px.data.tips()

page = vm.Page(
    title="Cross-filter from graph to table",
    components=[
        vm.Graph(
            title="Click on a box to use that box's sex to filter table",
            figure=px.density_heatmap(tips, x="total_bill", y="tip"),
            actions=[
                va.set_control(control="total_bill_filter", value="x"),
                va.set_control(control="tip_filter", value="y"),
            ],
        ),
        vm.AgGrid(id="tips_table", figure=dash_ag_grid(tips)),  # (1)!
    ],
    controls=[
        vm.Filter(id="total_bill_filter", column="total_bill", targets=["tips_table"]),
        vm.Filter(id="tip_filter", column="tip", targets=["tips_table"]),
    ],  # (2)!
)

dashboard = vm.Dashboard(pages=[page])

print(dashboard.model_dump())
# Vizro().build(dashboard).run()
