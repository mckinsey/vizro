"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture

df = px.data.iris()


@capture("action")
def update_card_text(species):
    """Returns the input value."""
    return f"You selected species {species}"


vm.Page.add_type("components", vm.RadioItems)

page = vm.Page(
    title="Action with value as input",
    layout=vm.Layout(grid=[[0, 1]]),
    components=[
        vm.RadioItems(
            id="my_selector",
            title="Select a species:",
            options=df["species"].unique().tolist(),
            actions=[
                vm.Action(function=update_card_text(), inputs=["my_selector.value"], outputs=["my_card.children"])
            ],
        ),
        vm.Card(text="Placeholder text", id="my_card"),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
