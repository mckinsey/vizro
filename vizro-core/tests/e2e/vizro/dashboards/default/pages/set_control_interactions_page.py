import e2e.vizro.constants as cnst
from custom_actions.custom_actions import scatter_click_data_custom_action

import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions import set_control
from vizro.tables import dash_ag_grid

iris = px.data.iris()
gapminder = px.data.gapminder()


set_control_graph_interactions_page = vm.Page(
    title=cnst.SET_CONTROL_GRAPH_INTERACTIONS_PAGE,
    layout=vm.Grid(grid=[[0], [2], [1]]),
    components=[
        vm.Graph(
            id=cnst.SCATTER_SET_CONTROL_INTERACTIONS_ID,
            figure=px.scatter(
                iris,
                x="sepal_length",
                y="petal_width",
                color="species",
                custom_data=["species"],
            ),
            actions=[
                set_control(control="filter_interactions", value="species"),
                vm.Action(
                    function=scatter_click_data_custom_action(),
                    inputs=[f"{cnst.SCATTER_SET_CONTROL_INTERACTIONS_ID}.clickData"],
                    outputs=f"{cnst.CARD_SET_CONTROL_INTERACTIONS_ID}",
                ),
            ],
        ),
        vm.Card(id=cnst.CARD_SET_CONTROL_INTERACTIONS_ID, text="### No data clicked."),
        vm.Graph(
            id=cnst.BOX_SET_CONTROL_INTERACTIONS_ID,
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
            targets=[cnst.BOX_SET_CONTROL_INTERACTIONS_ID],
            selector=vm.Dropdown(id=cnst.DROPDOWN_SET_CONTROL_INTER_FILTER),
        ),
        vm.Parameter(
            targets=[f"{cnst.BOX_SET_CONTROL_INTERACTIONS_ID}.title"],
            selector=vm.RadioItems(id=cnst.RADIOITEM_SET_CONTROL_INTER_PARAM, options=["red", "blue"], value="blue"),
        ),
    ],
)

set_control_ag_grid_interactions_page = vm.Page(
    title=cnst.SET_CONTROL_TABLE_AG_GRID_INTERACTIONS_PAGE,
    components=[
        vm.Container(
            components=[
                vm.AgGrid(
                    id=cnst.SET_CONTROL_TABLE_AG_GRID_INTERACTIONS_ID,
                    title="Table Country",
                    figure=dash_ag_grid(
                        id="set_control_ag_grid_table_country",
                        data_frame=gapminder,
                    ),
                    actions=[set_control(control="filter_continent", value="continent")],
                ),
            ],
            variant="filled",
        ),
        vm.Container(
            components=[
                vm.Graph(
                    id=cnst.SET_CONTROL_LINE_AG_GRID_INTERACTIONS_ID,
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
            column="year",
            targets=[cnst.SET_CONTROL_TABLE_AG_GRID_INTERACTIONS_ID],
            selector=vm.Dropdown(value=2007),
        ),
        vm.Filter(
            id="filter_continent",
            column="continent",
            targets=[cnst.SET_CONTROL_LINE_AG_GRID_INTERACTIONS_ID],
            selector=vm.RadioItems(options=["Europe", "Africa", "Americas"]),
        ),
    ],
)
