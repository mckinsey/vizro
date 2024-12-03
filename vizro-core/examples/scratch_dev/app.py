from typing import List, Literal

import vizro.models as vm
import vizro.plotly.express as px
from dash import html
from vizro import Vizro
from vizro._themes._color_values import COLORS

df = px.data.gapminder()


page = vm.Page(
    title="Charts UI",
    components=[
        vm.Card(text="Foo"),
        vm.Graph(
            id="gapminder",
            figure=px.bar(
                df,
                x="continent",
                y="gdpPercap",
            ),
        ),
    ],
    controls=[
        vm.Filter(
            targets=["gapminder"],
            column="continent",
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
