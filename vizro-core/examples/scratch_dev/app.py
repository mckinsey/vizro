"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px
from charts.charts import page2
from vizro.managers import data_manager

df = px.data.iris()

data_manager["iris"] = px.data.iris()

page = vm.Page(
    title="Test",
    layout=vm.Layout(
        grid=[[0, 1], [2, 3], [4, 5]],
    ),
    components=[
        vm.Card(
            text="""
        ### What is Vizro?

        Vizro is a toolkit for creating modular data visualization applications.
        """
        ),
        vm.Card(
            text="""
                ### Github

                Checkout Vizro's github page.
            """,
            href="https://github.com/mckinsey/vizro",
        ),
        vm.Card(
            text="""
                ### Docs

                Visit the documentation for codes examples, tutorials and API reference.
            """,
            href="https://vizro.readthedocs.io/",
        ),
        vm.Card(
            text="""
                ### Nav Link

                Click this for page 2.
            """,
            href="/page2",
        ),
        vm.Graph(id="scatter_chart", figure=px.scatter("iris", x="sepal_length", y="petal_width", color="species")),
        vm.Graph(id="hist_chart", figure=px.histogram("iris", x="sepal_width", color="species")),
    ],
    controls=[
        vm.Filter(column="species", selector=vm.Dropdown(value=["ALL"])),
        vm.Filter(column="petal_length"),
        vm.Filter(column="sepal_width"),
    ],
)

dashboard = vm.Dashboard(pages=[page, page2])

if __name__ == "__main__":
    from vizro import Vizro

    string = dashboard._to_python(extra_imports={"from dash_ag_grid import AgGrid"})
    print(string)  # noqa

    Vizro().build(dashboard).run()
