"""Dev app to try things out."""

import vizro.models as vm
from vizro import Vizro

page = vm.Page(
    title="Test page",
    components=[
        vm.Card(
            text="Card with all components",
            title="Card title",
            header="This is card header",
            footer="This is card footer",
            description="Tooltip",
        ),
        vm.Card(
            title="Card title",
            text="Card with just title",
        ),
        vm.Card(
            header="This is card header",
            text="Lorem Ipsum is simply dummy text of the printing and typesetting industry. "
            "Lorem Ipsum has been the industry's standard dummy text ever since the 1500s.",
        ),
        vm.Card(
            text="Card without header",
            title="Card title",
            footer="This is card footer",
            description="Tooltip",
        ),
        vm.Card(
            text="Regular card with only text",
        ),
        vm.Card(
            text="Card without title",
            header="This is card header",
            footer="This is card footer",
            description="Tooltip",
        ),
    ],
    layout=vm.Grid(
        grid=[
            [0, 1, 2, 3],
            [4, 5, -1, -1],
            [-1, -1, -1, -1],
            [-1, -1, -1, -1],
        ]
    ),
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
