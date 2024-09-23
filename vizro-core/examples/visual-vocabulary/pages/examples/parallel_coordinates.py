import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

iris = px.data.iris()

page = vm.Page(
    title="Parallel coordinates",
    components=[
        vm.Graph(
            figure=px.parallel_coordinates(
                iris, color="species_id", dimensions=["sepal_width", "sepal_length", "petal_width", "petal_length"]
            )
        )
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
