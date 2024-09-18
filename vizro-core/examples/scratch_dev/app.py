"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture

iris = px.data.iris()


@capture("action")
def update_graph_title(value):
    """Custom action."""
    return f"Distribution for {value}"


page = vm.Page(
    title="Dynamic Graph title",
    components=[
        vm.Graph(
            id="my-graph", title="Distribution for setosa", figure=px.bar(iris, x="sepal_length", y="sepal_width")
        ),
    ],
    controls=[
        vm.Filter(
            column="species",
            selector=vm.Dropdown(
                id="my-dropdown",
                multi=False,
                title="Select species:",
                value="setosa",
                actions=[
                    vm.Action(
                        function=update_graph_title(), inputs=["my-dropdown.value"], outputs=["my-graph-title.children"]
                    )
                ],
            ),
        )
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
