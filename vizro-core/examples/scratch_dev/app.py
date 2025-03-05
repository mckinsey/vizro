"""Test app"""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid, dash_data_table

iris = px.data.iris()

page = vm.Page(
    title="AgGrid",
    components=[
        vm.AgGrid(figure=dash_ag_grid(iris)),
        vm.Container(
            title="Container II",
            components=[vm.AgGrid(figure=dash_ag_grid(iris))],
            variant="filled",
        ),
    ],
)

page_two = vm.Page(
    title="Data Table",
    components=[
        vm.Table(figure=dash_data_table(iris)),
        vm.Container(
            title="Container II",
            components=[vm.Table(figure=dash_data_table(iris))],
            variant="filled",
        ),
    ],
)

page_three = vm.Page(
    title="Graph",
    components=[
        vm.Graph(figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species")),
        vm.Container(
            title="Container II",
            components=[vm.Graph(figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species"))],
            variant="filled",
        ),
    ],
)

page_four = vm.Page(
    title="Card",
    components=[vm.Card(text="""Hello"""), vm.Card(text="""Hello"""), vm.Card(text="""Hello""")],
)
dashboard = vm.Dashboard(pages=[page, page_two, page_three, page_four])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
