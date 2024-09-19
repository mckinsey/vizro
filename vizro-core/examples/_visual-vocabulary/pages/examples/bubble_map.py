import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

carshare = px.data.carshare()

page = vm.Page(
    title="Bubble map",
    components=[
        vm.Graph(
            figure=px.scatter_map(
                carshare,
                lat="centroid_lat",
                lon="centroid_lon",
                size="car_hours",
                size_max=15,
                opacity=0.5,
                zoom=10,
            )
        )
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
