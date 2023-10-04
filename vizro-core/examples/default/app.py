"""Example to show dashboard configuration."""
import os
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
    controls: List[ControlType] = []

    def build(self):
        return html.Div(
            [html.H4(self.title), html.Hr()] + [control.build() for control in self.controls],
            className="control_group_container",
        )


vm.Page.add_type("controls", ControlGroup)
# ControlGroup.update_forward_refs(Filter=vm.Filter, Parameter=vm.Parameter)

page1 = vm.Page(
    title="Relationship Analysis",
    components=[
        vm.Graph(
            id="scatter_relation",
            figure=px.scatter(df_gapminder, x="gdpPercap", y="lifeExp", size="pop"),
        ),
    ],
    controls=[
        ControlGroup(
            title="Group A",
            controls=[
                vm.Parameter(
                    targets=["scatter_relation.x"],
                    selector=vm.Dropdown(
                        options=["lifeExp", "gdpPercap", "pop"], multi=False, value="gdpPercap", title="Choose x-axis"
                    ),
                ),
                vm.Parameter(
                    targets=["scatter_relation.y"],
                    selector=vm.Dropdown(
                        options=["lifeExp", "gdpPercap", "pop"], multi=False, value="lifeExp", title="Choose y-axis"
                    ),
                ),
            ],
        ),
        ControlGroup(
            title="Group B",
            controls=[
                vm.Parameter(
                    targets=["scatter_relation.size"],
                    selector=vm.Dropdown(
                        options=["lifeExp", "gdpPercap", "pop"], multi=False, value="pop", title="Choose bubble size"
                    ),
                )
            ],
        ),
    ],
)

page2 = vm.Page(title="Second Page", components=[vm.Button()])
dashboard = vm.Dashboard(pages=[page1, page2])


if __name__ == "__main__":
    Vizro._user_assets_folder = os.path.abspath("../assets")
    Vizro().build(dashboard).run()
