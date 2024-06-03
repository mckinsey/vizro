"""Example to show dashboard configuration."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

df = px.data.iris()

page = vm.Page(
    title="My first dashboard",
    components=[
        # components consist of vm.Graph or  vm.Table
        vm.Graph(id="scatter_chart", figure=px.scatter(df, x="sepal_length", y="petal_width", color="species")),
        vm.Graph(id="hist_chart", figure=px.histogram(df, x="sepal_width", color="species")),
    ],
    controls=[
        # controls consist of vm.Filter or vm.Parameter
        # filter the dataframe (df) of the target graph (histogram), by column sepal_width, using the dropdown
        vm.Filter(column="sepal_width", selector=vm.Dropdown(), targets=["hist_chart"]),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
