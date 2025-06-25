import numpy as np

from vizro import Vizro
import vizro.models as vm
import pandas as pd
import vizro.plotly.express as px

iris = px.data.iris()


graphs = vm.Page(
    title="Graphs",
    components=[
        vm.Graph(
            figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species"),
            title="Relationships between Sepal Width and Sepal Length",
            header="""
                Each point in the scatter plot represents one of the 150 iris flowers, with colors indicating their
                types. The Setosa type is easily identifiable by its short and wide sepals.

                However, there is still overlap between the Versicolor and Virginica types when considering only sepal
                width and length.
                """,
            footer="""SOURCE: **Plotly iris data set, 2024**""",
        ),
    ],
)

tooltip = vm.Page(
    title="Tooltip",
    layout=vm.Grid(grid=[[0], [0], [1], [1], [1], [1], [1], [1], [2]]),
    components=[
        vm.Card(
            text="""
                The `description` argument enables you to add helpful context to your components by displaying an
                info icon next to its title. Hovering over the icon reveals a tooltip with the text you provide.

                Tooltips can be added to any Vizro component that has a `title` argument.
                You can provide a string to use the default info icon or `Tooltip` model to use any icon from the
                [Google Material Icons library](https://fonts.google.com/icons).
                Tooltips provide clean and lightweight way to add additional details to your dashboard.
            """
        ),
        vm.Graph(
            title="Relationships between Sepal Width and Sepal Length",
            figure=px.scatter(
                iris,
                x="sepal_width",
                y="sepal_length",
                color="species",
                size="petal_length",
            ),
            description="""
                **The Iris dataset** includes measurements of 150 iris flowers across three types: Setosa, Versicolor,
                and Virginica.
                While all samples are labeled by type, they can appear similar when looking at just some features -
                 making it a useful dataset for exploring patterns and challenges in classification.
            """,
        ),
        vm.Button(
            text="Export data",
            description="""
                Use this button to export the filtered data from the Iris dataset.
            """,
        ),
    ],
    controls=[
        vm.Filter(
            column="species",
            selector=vm.Dropdown(
                title="Species",
                description="""
                    Select one or more species to explore patterns
                    specific to Setosa, Versicolor, or Virginica.
                """,
            ),
        ),
        vm.Filter(
            column="sepal_width",
            selector=vm.RangeSlider(
                description="""
                    Use the slider to filter flowers by sepal width.
                    Only samples within the selected range will be shown.
                """
            ),
        ),
    ],
    description="""
        This page provides overview of Tooltip functionality.
    """,
)


dashboard = vm.Dashboard(pages=[graphs, tooltip])

if __name__ == "__main__":
    app = Vizro().build(dashboard)
    app.run()
