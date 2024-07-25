import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

iris = px.data.iris()

page = vm.Page(
    title="Scatter",
    components=[vm.Graph(figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species"))],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
