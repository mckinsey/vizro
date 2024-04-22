"""Example to show dashboard configuration."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid, dash_data_table

df = px.data.iris()

page = vm.Page(
    title="My first dashboard",
    components=[
        vm.Graph(
            id="scatter_chart",
            figure=px.scatter(df, x="sepal_length", y="petal_width", color="species", title="Title - Plotly Chart"),
        ),
        vm.AgGrid(title="Title - AG Grid", figure=dash_ag_grid(data_frame=df)),
        vm.Table(title="Title - DataTable", figure=dash_data_table(data_frame=df)),
    ],
    controls=[
        vm.Filter(column="species", selector=vm.Dropdown(value=["ALL"])),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
