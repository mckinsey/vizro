"""Scratchpad for testing."""

import vizro.models as vm
from vizro import Vizro

page = vm.Page(
    title="Button with variants",
    layout=vm.Flex(direction="row"),
    components=[vm.Button(variant="filled"), vm.Button(variant="outlined"), vm.Button(variant="plain")],
)

dashboard = vm.Dashboard(pages=[page])


if __name__ == "__main__":
    Vizro().build(dashboard).run()
