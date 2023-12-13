import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import filter_interaction
from vizro.models.types import capture


@capture("action")
def my_custom_action(show_species: bool, scatter_chart_clickData: dict):
    """Custom action."""
    clicked_point = scatter_chart_clickData["points"][0]
    x, y = clicked_point["x"], clicked_point["y"]
    text = f"Clicked point has sepal length {x}, petal width {y}"

    if show_species:
        species = clicked_point["customdata"][0]
        text += f" and species {species}"
    return text


df = px.data.iris()

page = vm.Page(
    title="Example of a custom action with UI inputs and outputs",
    layout=vm.Layout(
        grid=[
            [0, 2],
            [0, 2],
            [0, 2],
            [1, -1],
        ],
        row_gap="25px",
    ),
    components=[
        vm.Graph(
            id="scatter_chart",
            figure=px.scatter(df, x="sepal_length", y="petal_width", color="species", custom_data=["species"]),
            actions=[
                vm.Action(function=filter_interaction(targets=["scatter_chart_2"])),
                vm.Action(
                    function=my_custom_action(show_species=True),
                    inputs=["scatter_chart.clickData"],
                    outputs=["my_card.children"],
                ),
            ],
        ),
        vm.Card(id="my_card", text="Click on a point on the above graph."),
        vm.Graph(
            id="scatter_chart_2",
            figure=px.scatter(df, x="sepal_length", y="petal_width", color="species"),
        ),
    ],
    controls=[vm.Filter(column="species", selector=vm.Dropdown(title="Species"))],
)

dashboard = vm.Dashboard(pages=[page])

Vizro().build(dashboard).run()
