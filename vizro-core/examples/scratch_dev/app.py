"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro


# Comment to restart the CI
df = px.data.iris()


# Enable vm.Filter object to be used within the "Page.components"
vm.Page.add_type("components", vm.Filter)
vm.Page.add_type("components", vm.Parameter)

page_1 = vm.Page(
    title="Page 1",
    controls=[
        # DOES NOT work from the main branch
        vm.Filter(column="species", targets=["graph"]),
        vm.Parameter(targets=["graph.x"], selector=vm.RadioItems(options=["sepal_length", "sepal_width"])),
        # WORKS from the main branch
        vm.Filter(column="species"),
    ],
    components=[
        # DOES NOT work from the main branch
        vm.Filter(column="species", targets=["graph"]),
        vm.Parameter(targets=["graph.y"], selector=vm.RadioItems(options=["sepal_length", "sepal_width"])),
        # Graph
        vm.Graph(id="graph", figure=px.scatter(df, x="sepal_length", y="petal_length", color="species")),
        # WORKS from the main branch
        vm.Filter(column="species", targets=["graph"]),
        vm.Parameter(targets=["graph.color"], selector=vm.RadioItems(options=["species", "petal_width"])),
    ],
)

dashboard = vm.Dashboard(pages=[page_1])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
