"""Dev app to try things out."""

import dash_bootstrap_components as dbc

import vizro.models as vm
from vizro import Vizro
import vizro.plotly.express as px


from typing import Literal

gapminder = px.data.gapminder()


class NumberInput(vm.VizroBaseModel):
    type: Literal["number_input"] = "number_input"

    def build(self):
        return (
            dbc.Input(
                id="number-input",
                type="number",
                min=0,
                max=10,
                step=1,
                value=5,
                debounce=True,
            ),
        )


vm.Page.add_type("components", NumberInput)

page = vm.Page(
    title="Charts UI",
    components=[
        NumberInput(),
        vm.Graph(figure=px.box(gapminder, x="year", y="gdpPercap", color="continent")),
    ],
    controls=[vm.Filter(column="year")],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
