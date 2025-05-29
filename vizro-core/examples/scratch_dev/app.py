"""Custom filter action."""

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture


@capture("action")
def custom_action(value):
    return str(value)


df = px.data.iris()


page = vm.Page(
    title="Charts UI",
    components=[
        vm.Graph(figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species")),
        vm.Card(id="card-id", text="Blah"),
    ],
    controls=[
        vm.Filter(
            column="species",
            selector=vm.RadioItems(
                id="radio_items",
                options=[1, 2, 3],
                actions=[
                    # Action is defined in the old fashion way so that the example can be easily reused with the
                    # vizro==0.1.37 (Checkout to -> c01752a000d1b8a70fd310775358825215794fc7) to prove that it works.
                    vm.Action(
                        function=custom_action(),
                        inputs=["radio_items.value"],
                        outputs=["card-id.children"],
                    )
                ],
            ),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
