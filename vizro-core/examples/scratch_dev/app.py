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

dashboard = vm.Dashboard(pages=[graphs])

if __name__ == "__main__":
    app = Vizro().build(dashboard)
    app.run()
