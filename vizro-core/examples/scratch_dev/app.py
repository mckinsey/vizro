"""There are 8 cases that should be covered:
* Page
=== components
1. ------ Filter -> vm.Page
2. ------ Filter in ControlGroup -> vm.Page

=== controls
3. ------ Filter -> vm.Page
4. ------ Filter in ControlGroup -> vm.Page

* Container
=== components
5. ------ Filter -> vm.Container
6. ------ Filter in ControlGroup -> vm.Container

===--- controls
7. ------ Filter -> vm.Container
8. ------ Filter in ControlGroup -> vm.Container
"""

from typing import List, Literal

from dash import html

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import ControlType

df_gapminder = px.data.gapminder()


class ControlGroup(vm.VizroBaseModel):
    """Container to group controls."""

    type: Literal["control_group"] = "control_group"
    title: str
    controls: list[ControlType] = []

    def build(self):
        return html.Div(
            [html.H4(self.title), html.Hr()] + [control.build() for control in self.controls],
            className="control_group_container",
        )


vm.Page.add_type("controls", ControlGroup)
vm.Page.add_type("components", ControlGroup)
vm.Page.add_type("components", vm.Filter)

vm.Container.add_type("controls", ControlGroup)
vm.Container.add_type("components", ControlGroup)
vm.Container.add_type("components", vm.Filter)

page = vm.Page(
    layout=vm.Flex(),
    title="Page:",
    components=[
        vm.Filter(id="page_components", column="country"),
        ControlGroup(
            title="page_components_group",
            controls=[vm.Filter(id="page_components_group", column="continent")],
        ),
        vm.Container(
            title="Container:",
            components=[
                vm.Filter(id="container_components", column="country"),
                ControlGroup(
                    title="container_components_group",
                    controls=[vm.Filter(id="container_components_group", column="continent")],
                ),
                vm.Graph(id="scatter", figure=px.scatter(df_gapminder, x="gdpPercap", y="lifeExp", size="pop")),
            ],
            controls=[
                vm.Filter(id="container_controls", column="country"),
                ControlGroup(
                    title="container_controls_group",
                    controls=[vm.Filter(id="container_controls_group", column="continent")],
                ),
            ],
        ),
    ],
    controls=[
        vm.Filter(id="page_controls", column="continent"),
        ControlGroup(
            title="page_controls_group",
            controls=[
                vm.Filter(id="page_controls_group", column="country"),
            ],
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])
if __name__ == "__main__":
    Vizro().build(dashboard).run()
