"""This is a test app to test the dashboard layout."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
import dash_bootstrap_components as dbc

df = px.data.iris()

page = vm.Page(
    title="Bootstrap theme inside Vizro app",
    layout=vm.Grid(grid=[[0, 1], [2, 2], [2, 2], [3, 3], [3, 3]]),
    components=[
        vm.Card(
            text="""
                ### What is Vizro?
                An open-source toolkit for creating modular data visualization applications.

                Rapidly self-serve the assembly of customized dashboards in minutes - without the need for advanced coding or design experience - to create flexible and scalable, Python-enabled data visualization applications."""
        ),
        vm.Card(
            text="""
                ### Github

                Checkout Vizro's GitHub page for further information and release notes. Contributions are always welcome!""",
            href="https://github.com/mckinsey/vizro",
        ),
        vm.Graph(id="scatter_chart", figure=px.scatter(df, x="sepal_length", y="petal_width", color="species")),
        vm.Graph(id="hist_chart", figure=px.histogram(df, x="sepal_width", color="species")),
    ],
    controls=[vm.Filter(column="species"), vm.Filter(column="petal_length"), vm.Filter(column="sepal_width")],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
