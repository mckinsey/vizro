"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px
from custom_charts import waterfall
from pages._pages_utils import waterfall_data
from vizro import Vizro

df = px.data.iris()

page = vm.Page(
    title="Page with testing",
    layout=vm.Layout(grid=[[0, 1]]),
    components=[
        vm.Graph(
            figure=waterfall(
                waterfall_data, x="x", y="y", measure=["relative", "relative", "total", "relative", "relative", "total"]
            )
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
