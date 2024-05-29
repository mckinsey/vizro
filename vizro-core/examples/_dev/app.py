"""Example to show dashboard configuration."""

import vizro.models as vm
from vizro import Vizro

page = vm.Page(
    title="one_left_two_right",
    layout=vm.Layout(grid=[[0, 1], [0, 2]]),
    components=[
        vm.Card(id="comp-zero", text="""# Component 0"""),
        vm.Card(id="comp-one", text="""# Component 1"""),
        vm.Card(id="comp-two", text="""# Component 2"""),
    ],
)

dashboard = vm.Dashboard(pages=[page], theme="vizro_light")

if __name__ == "__main__":
    Vizro().build(dashboard).run()
