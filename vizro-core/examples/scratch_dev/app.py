"""Scratchpad for testing."""

import vizro.models as vm
from vizro import Vizro

page = vm.Page(
    title="Button with variants",
    layout=vm.Flex(direction="row"),
    components=[
        vm.Button(),
        vm.Button(variant="filled"),
        vm.Button(variant="outlined"),
        vm.Button(variant="plain"),
        vm.Button(extra={"color": "success"}),
        vm.Button(variant="outlined", extra={"color": "success"}),
    ],
)

dashboard = vm.Dashboard(pages=[page])


if __name__ == "__main__":
    Vizro().build(dashboard).run()
