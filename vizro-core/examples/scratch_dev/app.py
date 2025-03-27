import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture
from typing import Optional

df = px.data.iris()


@capture("action")
def custom_action_obtiene_seleccion(points_data: Optional[dict] = None):
    """Custom action."""
    clicked_point = points_data["points"][0]
    x = clicked_point["x"]
    text = f"Clicked point has sepal length {x}"
    return text, text


page = vm.Page(
    title="Action with clickData as input",
    components=[
        vm.Graph(
            id="scatter_chart",
            title="Title",
            footer="Footer",
            header="Header",
            figure=px.scatter(df, x="sepal_length", y="petal_width", color="species", custom_data=["species"]),
            actions=[
                vm.Action(
                    function=custom_action_obtiene_seleccion(),
                    inputs=["scatter_chart.clickData"],
                    outputs=["my_card.children", "scatter_chart_header.children"],
                ),
            ],
        ),
        vm.Card(id="my_card", text="Click on a point on the above graph."),
    ],
)
dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
