"""Dev app to try things out."""

import vizro.plotly.express as px
import vizro.models as vm
from vizro import Vizro

iris = px.data.iris()


page = vm.Page(
    title="Dynamic data from URL",
    components=[
        vm.Graph(
            id="page_3_graph_1",
            figure=px.scatter(iris, x="sepal_length", y="petal_length", color="species"),
        )
    ],
    controls=[
        vm.Filter(column="species", selector=vm.Checklist(show_select_all=False)),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
