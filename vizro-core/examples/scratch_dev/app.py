"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid, dash_data_table

iris = px.data.iris()
gapminder_2007 = px.data.gapminder().query("year == 2007")

page_graph = vm.Page(
    title="Formatted Graph",
    components=[
        vm.Graph(
            figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species"),
            title="Relationships between Sepal Width and Sepal Length",
            header="""
                Each point in the scatter plot represents one of the 150 iris flowers,  with colors indicating their
                types. The Setosa type is easily identifiable by its short and wide sepals.

                However, there is still overlap between the Versicolor and Virginica types when considering only sepal
                width and length.
                """,
            footer="""SOURCE: **Plotly iris data set, 2024**""",
        ),
    ],
)

page_grid = vm.Page(
    title="Formatted AgGrid",
    components=[
        vm.AgGrid(
            figure=dash_ag_grid(data_frame=gapminder_2007, dashGridOptions={"pagination": True}),
            title="Gapminder Data Insights",
            header="""#### An Interactive Exploration of Global Health, Wealth, and Population""",
            footer="""SOURCE: **Plotly gapminder data set, 2024**""",
        )
    ],
)

page_table = vm.Page(
    title="Formatted DataTable",
    components=[
        vm.Table(
            figure=dash_data_table(data_frame=gapminder_2007),
            title="Gapminder Data Insights",
            header="""#### An Interactive Exploration of Global Health, Wealth, and Population""",
            footer="""SOURCE: **Plotly gapminder data set, 2024**""",
        )
    ],
)


dashboard = vm.Dashboard(pages=[page_graph, page_grid, page_table])

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=False)
