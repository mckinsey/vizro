import e2e.vizro.constants as cnst

import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions import set_control
from vizro.tables import dash_ag_grid

iris = px.data.iris()
gapminder = px.data.gapminder()


cross_filter_graph_page = vm.Page(
    title=cnst.SET_CONTROL_GRAPH_CROSS_FILTER_PAGE,
    components=[
        vm.Graph(
            id=cnst.SCATTER_SET_CONTROL_CROSS_FILTER_ID,
            figure=px.scatter(
                iris,
                x="sepal_length",
                y="petal_width",
                color="species",
                custom_data=["species"],
            ),
            actions=[set_control(control="filter_interactions", value="species")],
        ),
        vm.Graph(
            id=cnst.BOX_SET_CONTROL_CROSS_FILTER_ID,
            figure=px.box(
                iris,
                x="sepal_length",
                y="petal_width",
                color="species",
            ),
        ),
    ],
    controls=[
        vm.Filter(
            id="filter_interactions",
            column="species",
            targets=[cnst.BOX_SET_CONTROL_CROSS_FILTER_ID],
            selector=vm.Dropdown(id=cnst.DROPDOWN_SET_CONTROL_CROSS_FILTER),
        )
    ],
)

cross_filter_ag_grid_page = vm.Page(
    title=cnst.SET_CONTROL_TABLE_AG_GRID_CROSS_FILTER_PAGE,
    components=[
        vm.Container(
            components=[
                vm.AgGrid(
                    id=cnst.SET_CONTROL_TABLE_AG_GRID_CROSS_FILTER_ID,
                    title="Table Country",
                    figure=dash_ag_grid(
                        id="set_control_ag_grid_table_country",
                        data_frame=gapminder[gapminder["year"] == 2007],
                    ),
                    actions=[set_control(control="filter_continent", value="continent")],
                ),
            ],
            variant="filled",
        ),
        vm.Container(
            components=[
                vm.Graph(
                    id=cnst.SET_CONTROL_LINE_AG_GRID_CROSS_FILTER_ID,
                    figure=px.line(
                        gapminder,
                        title="Line Country",
                        x="year",
                        y="gdpPercap",
                        markers=True,
                    ),
                ),
            ],
            variant="filled",
        ),
    ],
    controls=[
        vm.Filter(
            id="filter_continent",
            column="continent",
            targets=[cnst.SET_CONTROL_LINE_AG_GRID_CROSS_FILTER_ID],
            selector=vm.RadioItems(options=["Europe", "Africa", "Americas"], value="Africa"),
        ),
    ],
)


cross_filter_card_graph_page = vm.Page(
    title=cnst.SET_CONTROL_CARD_GRAPH_CROSS_FILTER_PAGE,
    components=[
        vm.Card(
            id=cnst.SET_CONTROL_CARD_GRAPH_CROSS_FILTER_CARD_ID,
            text="Continent to choose: Oceania",
            actions=set_control(control="card-filter", value="Oceania"),
        ),
        vm.Graph(
            id="box-card-graph-id",
            figure=px.box(
                gapminder,
                x="country",
                y="pop",
                color="continent",
            ),
        ),
    ],
    controls=[
        vm.Filter(
            id="card-filter",
            column="continent",
            targets=["box-card-graph-id"],
            selector=vm.RadioItems(id=cnst.SET_CONTROL_CARD_GRAPH_CROSS_FILTER_CONTOL_ID),
        )
    ],
)
