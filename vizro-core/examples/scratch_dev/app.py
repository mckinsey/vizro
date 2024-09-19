"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

iris = px.data.iris()

page = vm.Page(
    title="Page with different font",
    components=[
        vm.Card(
            text="""
        # Lorem ipsum

        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam nec nunc nec libero ultricies ultricies.
        """
        ),
        vm.Graph(figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species")),
    ],
)

dashboard = vm.Dashboard(pages=[page], title="Dashboard title")

if __name__ == "__main__":
    Vizro().build(dashboard).run()
