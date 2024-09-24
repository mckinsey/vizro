"""Dev app to try things out."""

import plotly.io as pio
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

pio.templates["vizro_dark"]["layout"]["paper_bgcolor"] = "rgba(0, 0, 0, 0)"
pio.templates["vizro_light"]["layout"]["paper_bgcolor"] = "rgba(0, 0, 0, 0)"
pio.templates["vizro_dark"]["layout"]["plot_bgcolor"] = "rgba(0, 0, 0, 0)"
pio.templates["vizro_light"]["layout"]["plot_bgcolor"] = "rgba(0, 0, 0, 0)"


iris = px.data.iris()

page = vm.Page(
    title="Page with subsections",
    layout=vm.Layout(grid=[[0, 1]]),
    components=[
        vm.Container(
            title="Container I",
            components=[vm.Graph(figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species"))],
        ),
        vm.Container(
            title="Container II",
            components=[vm.Graph(figure=px.box(iris, x="species", y="sepal_length", color="species"))],
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=False)
