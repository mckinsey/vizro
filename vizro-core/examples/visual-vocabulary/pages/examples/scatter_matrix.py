import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

iris = px.data.iris()

page = vm.Page(
    title="Scatter matrix",
    components=[
        vm.Graph(
            figure=px.scatter_matrix(iris, dimensions=["sepal_length", "sepal_width", "petal_length", "petal_width"])
        )
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
