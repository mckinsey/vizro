import e2e.vizro.constants as cnst

import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions import filter_interaction
from vizro.tables import dash_ag_grid

gapminder = px.data.gapminder()

ag_grid_interactions_page = vm.Page(
    title=cnst.TABLE_AG_GRID_INTERACTIONS_PAGE,
    components=[
        vm.AgGrid(
            id=cnst.TABLE_AG_GRID_INTERACTIONS_ID,
            title="Table Country",
            figure=dash_ag_grid(
                id="ag_grid_table_country",
                data_frame=gapminder,
            ),
            actions=[
                vm.Action(
                    function=filter_interaction(
                        targets=[
                            cnst.LINE_AG_GRID_INTERACTIONS_ID,
                        ]
                    )
                )
            ],
        ),
        vm.Graph(
            id=cnst.LINE_AG_GRID_INTERACTIONS_ID,
            figure=px.line(
                gapminder,
                title="Line Country",
                x="year",
                y="gdpPercap",
                markers=True,
            ),
        ),
    ],
    controls=[
        vm.Filter(
            column="year",
            targets=[cnst.TABLE_AG_GRID_INTERACTIONS_ID],
            selector=vm.Dropdown(value=2007),
        ),
        vm.Filter(
            column="continent",
            targets=[cnst.TABLE_AG_GRID_INTERACTIONS_ID],
            selector=vm.RadioItems(options=["Europe", "Africa", "Americas"]),
        ),
    ],
)
