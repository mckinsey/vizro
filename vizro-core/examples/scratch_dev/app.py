"""Scratchpad for testing."""

import vizro.models as vm
from vizro import Vizro

page = vm.Page(
    title="Buttons with different styles",
    layout=vm.Flex(direction="row"),
    components=[
        vm.Button(text="default"),
        vm.Button(text="filled", variant="filled"),
        vm.Button(text="outlined", variant="outlined"),
        vm.Button(text="plain", variant="plain"),
        vm.Button(extra={"color": "success"}),
        vm.Button(variant="outlined", extra={"color": "success"}),
    ],
)

dashboard = vm.Dashboard(pages=[page])


if __name__ == "__main__":
    Vizro().build(dashboard).run()
