# TODO[1.0.0]: delete this file. It is Dash-DataTable-backed e2e coverage (dash_data_table) plus filter_interaction,
#  both removed in 1.0.0. Also unwire it from dashboard.py (import + pages list + AG_GRID_ACCORDION nav) and drop the
#  golden screenshot for test_table_interactions_page.
import e2e.vizro.constants as cnst

import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions import filter_interaction
from vizro.tables import dash_data_table

gapminder = px.data.gapminder()

table_interactions_page = vm.Page(
    title=cnst.TABLE_INTERACTIONS_PAGE,
    components=[
        vm.Table(
            id=cnst.TABLE_INTERACTIONS_ID,
            title="Table Country",
            figure=dash_data_table(
                id="dash_data_table_country",
                data_frame=gapminder,
            ),
            actions=filter_interaction(targets=[cnst.LINE_INTERACTIONS_ID]),
        ),
        vm.Graph(
            id=cnst.LINE_INTERACTIONS_ID,
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
