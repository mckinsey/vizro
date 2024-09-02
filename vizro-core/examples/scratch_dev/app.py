"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro


iris = px.data.iris()

page = vm.Page(
    title="My first page",
    components=[
        vm.Graph(
            id="scatter_chart",
            figure=px.scatter(iris, title="My scatter chart", x="sepal_length", y="petal_width", color="species"),
        ),
    ],
    controls=[
        vm.Parameter(
            targets=["scatter_chart.title"],
            selector=vm.Dropdown(
                options=[
                    {"value": "Shipping Address State", "label": "State"},
                    {"value": "Category", "label": "Category"},
                    {"value": "Short_Title", "label": "Product item"},
                ],
                multi=False,
            ),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
