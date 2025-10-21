"""Dev app to try things out."""

import vizro.plotly.express as px
import vizro.models as vm
from vizro import Vizro
import vizro.actions as va

gapminder = px.data.gapminder()

page = vm.Page(
    title="Test page",
    components=[
        vm.Card(
            text="Lorem Ipsum is simply dummy text of the printing and typesetting industry. "
            "Lorem Ipsum has been the industry's standard dummy text ever since the 1500s.",
            header="### This is card header",
            footer="##### This is card footer",
            description="Tooltip",
        ),
        vm.Card(
            header="### This is card header",
            text="Lorem Ipsum is simply dummy text of the printing and typesetting industry. "
            "Lorem Ipsum has been the industry's standard dummy text ever since the 1500s.",
        ),
        vm.Card(
            text="Card with text and header and footer",
            header="### This is card header",
            footer="##### This is card footer",
        ),
        vm.Card(
            text="### Card with just text title",
        ),
        vm.Card(
            text="Card without header",
            footer="This is card footer",
            description="Tooltip",
        ),
        vm.Card(
            text="Regular card with only text",
        ),
        vm.Graph(figure=px.bar(gapminder, x="country", y="pop", color="continent")),
        vm.Card(
            text="Card with action",
            actions=va.set_control(control="filter-id-1", value="Europe"),
        ),
        vm.Card(
            text="Navigate to page",
            href="/dummy-page",
            # actions=va.set_control(control="filter-id-1", value="Europe")
        ),
    ],
    controls=[vm.Filter(id="filter-id-1", column="continent", selector=vm.RadioItems())],
    layout=vm.Grid(
        grid=[
            [0, 1, 2, 3],
            [4, 5, 7, 8],
            [6, 6, -1, -1],
            [6, 6, -1, -1],
        ]
    ),
)

page_2 = vm.Page(title="Dummy page", components=[vm.Card(text="This is plain old card.")])

dashboard = vm.Dashboard(pages=[page, page_2])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
