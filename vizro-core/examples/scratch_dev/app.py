"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro


carshare = px.data.carshare()

page_one = vm.Page(
    title="Scatter map",
    components=[
        vm.Graph(
            figure=px.scatter_map(
                carshare,
                lat="centroid_lat",
                lon="centroid_lon",
                color="peak_hour",
                size="car_hours",
                color_continuous_scale=px.colors.cyclical.IceFire,
                size_max=15,
                zoom=10,
            )
        ),
    ],
)

page_four = vm.Page(
    title="Density map",
    components=[
        vm.Graph(
            figure=px.density_map(
                carshare,
                lat="centroid_lat",
                lon="centroid_lon",
            )
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page_one, page_four])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
