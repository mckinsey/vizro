"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro


page = vm.Page(
    title="Incorrect color of selector 'x' clear selection",
    components=[
        vm.Graph(
            figure=px.scatter(px.data.iris(), x="sepal_width", y="sepal_length", color="species"),
        ),
    ],
    controls=[
        vm.Filter(column="species", selector=vm.Dropdown(multi=False)),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
