"""Rough example used by developers."""

import vizro.models as vm
from vizro import Vizro

page = vm.Page(
    title="Changing the card color",
    components=[
        vm.Card(id="my-card", text="""Lorem ipsum dolor sit amet consectetur adipisicing elit."""),
        vm.Card(text="""Lorem ipsum dolor sit amet consectetur adipisicing elit."""),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
