import e2e.vizro.constants as cnst

import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions import filter_interaction
from vizro.tables import dash_data_table

gapminder = px.data.gapminder()

table_interactions_page = vm.Page(
    title=cnst.TABLE_INTERACTIONS_PAGE,
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    id=cnst.TABLE_INTERACTIONS_CONTAINER,
                    title=cnst.TABLE_INTERACTIONS_CONTAINER,
                    components=[
                        vm.Table(
                            id=cnst.TABLE_INTERACTIONS_ID,
                            title="Table Country",
                            figure=dash_data_table(
                                id="dash_data_table_country",
                                data_frame=gapminder,
                            ),
                            actions=[
                                vm.Action(
                                    function=filter_interaction(
                                        targets=[
                                            cnst.LINE_INTERACTIONS_ID_ONE,
                                            cnst.LINE_INTERACTIONS_ID_TWO,
                                        ]
                                    )
                                )
                            ],
                        ),
                    ],
                ),
                vm.Container(
                    id=cnst.LINE_INTERACTIONS_CONTAINER_ONE,
                    title=cnst.LINE_INTERACTIONS_CONTAINER_ONE,
                    components=[
                        vm.Graph(
                            id=cnst.LINE_INTERACTIONS_ID_ONE,
                            figure=px.line(
                                gapminder,
                                title="Line Country",
                                x="year",
                                y="gdpPercap",
                                markers=True,
                            ),
                        ),
                    ],
                ),
            ]
        ),
        vm.Tabs(
            tabs=[
                vm.Container(
                    id=cnst.LINE_INTERACTIONS_CONTAINER_TWO,
                    title=cnst.LINE_INTERACTIONS_CONTAINER_TWO,
                    components=[
                        vm.Graph(
                            id=cnst.LINE_INTERACTIONS_ID_TWO,
                            figure=px.line(
                                gapminder,
                                title="Line Country",
                                x="year",
                                y="gdpPercap",
                                markers=True,
                            ),
                        ),
                    ],
                )
            ]
        ),
    ],
    controls=[
        vm.Filter(
            column="year",
            targets=[cnst.TABLE_INTERACTIONS_ID],
            selector=vm.Dropdown(value=2007),
        ),
        vm.Filter(
            column="continent",
            targets=[cnst.TABLE_INTERACTIONS_ID],
            selector=vm.RadioItems(options=["Europe", "Africa", "Americas"]),
        ),
    ],
)
