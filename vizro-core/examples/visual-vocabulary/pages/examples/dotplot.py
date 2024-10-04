import vizro.models as vm
import vizro.ployly.express as px
from vizro import Vizro

iris = px.data.iris()

page = vm.Page(
    title="Dot Plot",
    components=[vm.Graph(px.scatter(iris, x="sepal_length", y="species"))],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()