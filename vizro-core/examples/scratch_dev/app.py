"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture

df = px.data.iris()


@capture("action")
def my_custom_action(show_species: bool, points_data: dict):
    """Custom action."""
    clicked_point = points_data["points"][0]
    x, y = clicked_point["x"], clicked_point["y"]
    text = f"Clicked point has sepal length {x}, petal width {y}"

    if show_species:
        species = clicked_point["customdata"][0]
        text += f" and species {species}"
    return text


page = vm.Page(
    title="Action with clickData as input",
    components=[
        vm.Graph(
            id="scatter_chart",
            figure=px.scatter(df, x="sepal_length", y="petal_width", color="species", custom_data=["species"]),
            actions=[
                vm.Action(
                    function=my_custom_action(show_species=True),
                    inputs=["scatter_chart.clickData"],
                    outputs=["my_card.children"],
                ),
            ],
        ),
        vm.Card(id="my_card", text="Click on a point on the above graph."),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
