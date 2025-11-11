"""Dev app to try things out."""

from vizro import Vizro
import vizro.plotly.express as px
import vizro.models as vm

page = vm.Page(
    title="Example buttons",
    layout=vm.Flex(direction="row"),
    components=[
        vm.Button(text="Download", variant="plain"),
        vm.Button(text="Download", icon="Download", variant="plain"),
        vm.Button(text="", icon="Download", variant="plain"),
        vm.Button(text="Download", variant="filled"),
        vm.Button(text="Download", icon="Download", variant="filled"),
        vm.Button(text="", icon="Download", variant="filled"),
        vm.Button(text="Download", variant="outlined"),
        vm.Button(text="Download", icon="Download", variant="outlined"),
        vm.Button(text="", icon="Download", variant="outlined"),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
