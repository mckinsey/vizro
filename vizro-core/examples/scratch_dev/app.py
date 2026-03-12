"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px

from vizro import Vizro

df = px.data.iris()


page = vm.Page(
    title="Page Two",
    components=[
        vm.Graph(figure=px.histogram(df, x="sepal_length")),
    ],
    controls=[
        vm.ControlGroup(
            title="Filters",
            controls=[
                vm.Filter(column="species", selector=vm.Dropdown(variant="filled")),
                vm.Filter(column="sepal_length", selector=vm.Slider())
            ],
            variant="outlined",
            collapsed="True"
        ),
        vm.ControlGroup(
            title="Filters 2",
            controls=[
                vm.Filter(column="species", selector=vm.Dropdown(variant="filled")),
                vm.Filter(column="sepal_length", selector=vm.Slider())
            ],
            variant="outlined",
            collapsed="True"
        )
    ],
)


dashboard = vm.Dashboard(
    pages=[page],
    title="QB",
)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
