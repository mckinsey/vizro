import e2e.vizro.constants as cnst

import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions import update_targets

_gapminder = px.data.gapminder().query("year == 2007")

vm.Page.add_type("controls", vm.Button)

apply_controls_on_button_click_page = vm.Page(
    title=cnst.PAGE_APPLY_CONTROLS_ON_BUTTON_CLICK,
    components=[
        vm.Graph(
            id=f"{cnst.PAGE_APPLY_CONTROLS_ON_BUTTON_CLICK}_graph",
            figure=px.scatter(
                _gapminder,
                x="gdpPercap",
                y="lifeExp",
                size="pop",
                color="continent",
            ),
        ),
    ],
    controls=[
        vm.Filter(
            column="continent",
            targets=[f"{cnst.PAGE_APPLY_CONTROLS_ON_BUTTON_CLICK}_graph"],
            selector=vm.RadioItems(
                title="Filter that does NOT auto-apply, but is taken into account when its target Graph is updated.",
                actions=None,
            ),
        ),
        vm.Parameter(
            targets=[f"{cnst.PAGE_APPLY_CONTROLS_ON_BUTTON_CLICK}_graph.x"],
            selector=vm.RadioItems(
                title="Parameter that does NOT auto-apply, but is taken into account when its target Graph is updated.",
                options=["gdpPercap", "lifeExp"],
                actions=[],
            ),
        ),
        vm.Button(text="Apply controls", actions=update_targets()),
    ],
)
