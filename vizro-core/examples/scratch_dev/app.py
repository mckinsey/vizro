"""Dev app to try things out."""

import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
from vizro.actions import export_data

df = px.data.iris()

page_one = vm.Page(
    title="Page 1",
    layout=vm.Flex(),
    components=[
        vm.Container(
            title="Button Styles",
            layout=vm.Flex(direction="row"),
            components=[
                vm.Button(text="Primary", variant="filled"),
                vm.Button(text="Primary", icon="Download", variant="filled"),
                vm.Button(text="", icon="Download", variant="filled"),
                vm.Button(text="Secondary", variant="outlined"),
                vm.Button(text="Secondary", icon="Download", variant="outlined"),
                vm.Button(text="", icon="Download", variant="outlined"),
                vm.Button(text="Tertiary", variant="plain"),
                vm.Button(text="Tertiary", icon="Download", variant="plain"),
                vm.Button(text="", icon="Download", variant="plain"),
            ],
        ),
        vm.Container(
            title="Controls",
            controls=[
                vm.Filter(column="species"),
                vm.Filter(column="petal_length"),
                vm.Filter(column="sepal_width"),
            ],
            components=[
                vm.Graph(title="Graph Title", figure=px.histogram(df, x="sepal_width", color="species")),
                vm.Button(text="Export Data", actions=export_data()),
            ],
        ),
    ],
)


page_two = vm.Page(
    title="Page 2",
    components=[
        vm.Graph(title="Graph Title", figure=px.histogram(df, x="sepal_width", color="species")),
        vm.Button(text="Export Data", actions=export_data()),
    ],
    controls=[
        vm.Filter(column="species"),
        vm.Filter(column="petal_length"),
        vm.Filter(column="sepal_width"),
    ],
)

dashboard = vm.Dashboard(pages=[page_one, page_two])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
