import e2e.vizro.constants as cnst

import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions import set_controls
from vizro.tables import dash_ag_grid

gapminder = px.data.gapminder()

ag_grid_interactions_page = vm.Page(
    title=cnst.TABLE_AG_GRID_INTERACTIONS_PAGE,
    components=[
        vm.Table(
            id=cnst.TABLE_AG_GRID_INTERACTIONS_ID,
            title="Table Country",
            figure=dash_ag_grid(
                id="ag_grid_table_country",
                data_frame=gapminder,
            ),
            # Row-selection cross-filter: clicking a row sets the continent filter (replaces the removed
            # `filter_interaction`). This also restores the AG Grid row-selection checkboxes.
            actions=set_controls(controls=[cnst.FILTER_CONTINENT_AG_GRID_INTERACTIONS_ID], value="continent"),
        ),
        vm.Graph(
            id=cnst.LINE_AG_GRID_INTERACTIONS_ID,
            figure=px.line(
                gapminder,
                title="Line Country",
                x="year",
                y="gdpPercap",
                markers=True,
                render_mode="svg",
            ),
        ),
    ],
    controls=[
        vm.Filter(
            column="year",
            targets=[cnst.TABLE_AG_GRID_INTERACTIONS_ID],
            selector=vm.Dropdown(id=cnst.DROPDOWN_AG_GRID_INTERACTIONS_ID, value=2007),
        ),
        vm.Filter(
            id=cnst.FILTER_CONTINENT_AG_GRID_INTERACTIONS_ID,
            column="continent",
            targets=[cnst.TABLE_AG_GRID_INTERACTIONS_ID],
            selector=vm.RadioItems(
                id=cnst.RADIOITEMS_AG_GRID_INTERACTIONS_ID, options=["Europe", "Africa", "Americas"]
            ),
        ),
    ],
)
