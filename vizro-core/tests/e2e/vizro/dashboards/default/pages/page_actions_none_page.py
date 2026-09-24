import e2e.vizro.constants as cnst

import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions import update_targets

_gapminder = px.data.gapminder().query("year == 2007")

vm.Page.add_type("controls", vm.Button)

page_actions_none = vm.Page(
    title=cnst.PAGE_ACTIONS_NONE,
    components=[
        vm.Graph(
            id=cnst.PAGE_ACTIONS_NONE_GRAPH_ID,
            figure=px.scatter(
                _gapminder,
                x="gdpPercap",
                y="lifeExp",
                size="pop",
                color="continent",
            ),
        ),
        vm.Button(text="Load graph", actions=update_targets()),
    ],
    controls=[
        vm.Filter(
            column="continent",
            targets=[cnst.PAGE_ACTIONS_NONE_GRAPH_ID],
            selector=vm.Dropdown(actions=None),
        ),
    ],
    actions=None,
)
