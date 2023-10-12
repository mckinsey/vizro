# """Example to show custom action for collapse left side panel."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models import Action
from vizro.models.types import capture


@capture("action")
def collapse_the_panel(collapse_button_id_n_clicks):
    if collapse_button_id_n_clicks and collapse_button_id_n_clicks % 2 == 1:
        return {"left_side_style": {"display": "none"}}
    else:
        return {"left_side_style": None}


page = vm.Page(
    title="test_page",
    components=[
        vm.Graph(
            figure=px.box(
                px.data.gapminder(),
                x="continent",
                y="lifeExp",
                color="continent",
                title="Distribution per continent",
            ),
            id="the_graph"
        ),
        vm.Button(
            id="collapse_button_id",
            text="hide/unhide",
            actions=[
                vm.Action(
                    function=collapse_the_panel(),
                    inputs=["collapse_button_id.n_clicks"],
                    outputs=["left_side.style"],
                )
            ]
        )
    ],
    controls=[
        vm.Filter(column="year", selector=vm.RangeSlider(title="Select timeframe")),
    ],
)
dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
