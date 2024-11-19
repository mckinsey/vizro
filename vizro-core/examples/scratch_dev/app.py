"""Dev app to try things out."""

import vizro.models as vm
from vizro import Vizro


page = vm.Page(
    title="Button Styling",
    layout=vm.Layout(grid=[[0, 1]]),
    components=[
        vm.Button(),
        vm.Button(text="Take me home", href="/"),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
