"""Simple Vizro dashboard with a graph inside a container."""

import vizro.models as vm
from vizro import Vizro

page = vm.Page(
    title="Debug",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="A",
                    components=[vm.Text(text="AAA")],
                ),
                vm.Container(
                    title="B",
                    components=[vm.Text(text="BBB")],
                ),
            ],
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
