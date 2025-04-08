"""Scratchpad for testing."""

import vizro.models as vm
from vizro import Vizro

# Uncomment the below to see the warnings
layouts = [
    vm.Grid(grid=[[0]]),
    vm.Flex(),
    # vm.Layout(grid=[[0]]),
    {"type": "grid", "grid": [[0]]},
    {"type": "flex"},
    # {"grid": [[0]]},
]


pages_1 = [
    vm.Page(title=f"Page {i}", components=[vm.Card(text=f"`{layout!r}`")], layout=layout)
    for i, layout in enumerate(layouts)
]
pages_2 = [
    vm.Page(
        title=f"Page {i}",
        components=[vm.Container(title="Container", components=[vm.Card(text=f"`{layout!r}`")], layout=layout)],
    )
    for i, layout in enumerate(layouts, len(layouts))
]


dashboard = vm.Dashboard(pages=pages_1 + pages_2)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
