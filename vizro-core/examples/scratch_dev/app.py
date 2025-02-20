"""Dev app to try things out."""

from os import chown

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture
from vizro.tables import dash_ag_grid

df = px.data.iris()


@capture("ag_grid")
def my_custom_ag_grid(data_frame, chosen_columns, **kwargs):
    print(f"\nChosen column: {chosen_columns}\n")
    return dash_ag_grid(data_frame=data_frame[chosen_columns], **kwargs)()


page = vm.Page(
    title="Page with subsections",
    layout=vm.Layout(grid=[[0, 3, 3, 3, 4, 4], [1, 3, 3, 3, 4, 4], [2, 3, 3, 3, 4, 4]]),
    components=[
        vm.Card(text="""Hello, this is a card with a [link](https://www.google.com)"""),
        vm.Card(text="""Hello, this is a card with a [link](https://www.google.com)"""),
        vm.Card(text="""Hello, this is a card with a [link](https://www.google.com)"""),
        vm.Container(
            title="Container I",
            components=[
                vm.Graph(figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species")),
            ],
            background=True,
        ),
        vm.Container(
            title="Container II",
            components=[
                vm.Graph(figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species")),
            ],
            background=True,
        ),
    ],
)

page_two = vm.Page(
    title="Container",
    components=[
        vm.Container(
            title="Container III",
            components=[
                vm.Graph(figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species")),
            ],
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page, page_two])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
