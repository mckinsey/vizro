"""Example app to show all features of Vizro."""

# check out https://github.com/mckinsey/vizro for more info about Vizro
# and checkout https://vizro.readthedocs.io/en/stable/ for documentation

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

df = px.data.iris()

page = vm.Page(
    title="Vizro on PyCafe",
    layout=vm.Layout(
        grid=[[0, 0, 0, 1, 2, 3], [4, 4, 4, 4, 4, 4], [4, 4, 4, 4, 4, 4], [5, 5, 5, 5, 5, 5], [5, 5, 5, 5, 5, 5]],
        row_min_height="175px",
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
        vm.Graph(id="scatter_chart", figure=px.scatter(df, x="sepal_length", y="petal_width", color="species")),
        vm.Graph(id="hist_chart", figure=px.histogram(df, x="sepal_width", color="species")),
    ],
    controls=[
        vm.Filter(column="species", selector=vm.Dropdown(value=["ALL"])),
        vm.Filter(column="petal_length"),
        vm.Filter(column="sepal_width"),
    ],
)

page2 = vm.Page(
    title="Page2", components=[vm.Graph(id="hist_chart2", figure=px.histogram(df, x="sepal_width", color="species"))]
)

dashboard = vm.Dashboard(pages=[page, page2])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
