"""Dev app to try things out."""

import numpy as np
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

df = px.data.iris()

df["species_long"] = df["species"] + " is one common species you can select in the iris dataset."
df["species_one_long"] = np.where(
    df["species"] == "setosa", "setosa is one common species you can select in the iris dataset.", df["species"]
)
page = vm.Page(
    title="",
    components=[
        vm.Graph(
            id="graph_1",
            figure=px.scatter(df, title="Title", x="sepal_width", y="sepal_length", color="species"),
        ),
    ],
    controls=[
        vm.Filter(column="species"),
        vm.Filter(column="species_long"),
        vm.Filter(column="species_one_long"),
    ],
)


dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
