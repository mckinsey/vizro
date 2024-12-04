"""Dev app to try things out."""

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions._filter_action import _filter
from vizro.models._controls.filter import _filter_isin
from vizro.models.types import capture


df = px.data.iris()


page = vm.Page(
    title="Charts UI",
    components=[
        vm.Graph(id="graph_id", figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species")),
        vm.Card(id="card_id", text="Placeholder text"),
    ],
    controls=[
        vm.Filter(
            id="filter_id",
            column="species",
            targets=["graph_id"],
            selector=vm.Dropdown(
                id="filter_dropdown_id",
                value="setosa",
                multi=False,
                actions=[
                    vm.Action(
                        function=_filter(targets=["graph_id"], filter_column="species", filter_function=_filter_isin),
                    ),
                    vm.Action(
                        function=(capture("action"))(lambda value: value)(),
                        inputs=["filter_dropdown_id.value"],
                        outputs=["card_id.children"],
                    ),
                ],
            ),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
