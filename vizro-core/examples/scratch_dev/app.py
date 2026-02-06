"""Dev app to try things out."""

import plotly.io as pio
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture

# Modify template colorway - this will work
pio.templates["vizro_dark"].layout.colorway = ["#6929c4", "#2d9fea", "#de6da9"]

df = px.data.iris()


# Custom chart is required with update_layout call to modify properties that otherwise
# would not take effect due to vizro and/or plotly overwrites.
@capture("graph")
def custom_background_chart(data_frame):
    return px.scatter(
        data_frame,
        x="sepal_length",
        y="petal_width",
        color="species",
    ).update_layout(
        plot_bgcolor="black",
    )


page = vm.Page(
    title="Template properties test",
    layout=vm.Grid(grid=[[0, 1], [2, 2]]),
    components=[
        vm.Graph(
            figure=px.histogram(
                df,
                x="sepal_width",
                color="species",
            ),
            title="Graph with template colors (colorway works)",
        ),
        vm.Graph(
            figure=px.histogram(
                df, x="sepal_width", color="species", color_discrete_sequence=["#E7E247", "#4D5061", "#5C80BC"]
            ),
            title="Graph with custom colors (overrides template)",
        ),
        vm.Graph(
            figure=custom_background_chart(data_frame=df),
            title="Graph with custom background (chart-specific styling works)",
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
