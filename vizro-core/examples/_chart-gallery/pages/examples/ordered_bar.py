from typing import Optional

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture

tips = px.data.tips()


@capture("graph")
def ordered_histogram(data_frame, x: str, y: str, orientation: Optional[str] = None):
    """Custom bar chart function with ordered categories."""
    fig = px.histogram(data_frame, x=x, y=y, orientation=orientation)
    axis_update = fig.update_yaxes if orientation == "h" else fig.update_xaxes
    return axis_update(categoryorder="total descending")


page = vm.Page(
    title="Bar",
    components=[vm.Graph(figure=ordered_histogram(tips, x="total_bill", y="day", orientation="h"))],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
