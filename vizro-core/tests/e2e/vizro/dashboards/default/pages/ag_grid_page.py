import e2e.vizro.constants as cnst

import vizro.models as vm
import vizro.plotly.express as px
from vizro.tables import dash_ag_grid

gapminder = px.data.gapminder()

ag_grid_page = vm.Page(
    title=cnst.TABLE_AG_GRID_PAGE,
    components=[
        vm.Container(
            id=cnst.TABLE_AG_GRID_CONTAINER,
            title=cnst.TABLE_AG_GRID_CONTAINER,
            layout=vm.Layout(grid=[[0, 1]], col_gap="0px"),
            components=[
                vm.AgGrid(
                    id=cnst.TABLE_AG_GRID_ID,
                    title="Equal Title One",
                    figure=dash_ag_grid(data_frame=gapminder, dashGridOptions={"pagination": True}),
                ),
                vm.Graph(
                    id=cnst.BOX_AG_GRID_PAGE_ID,
                    figure=px.box(gapminder, x="continent", y="lifeExp", title="Equal Title One"),
                ),
            ],
        )
    ],
    controls=[
        vm.Filter(
            column="year",
            targets=[cnst.TABLE_AG_GRID_ID],
            selector=vm.Dropdown(value=2007),
        ),
        vm.Filter(
            column="continent",
            targets=[cnst.TABLE_AG_GRID_ID],
            selector=vm.RadioItems(options=["Europe", "Africa", "Americas"]),
        ),
        vm.Filter(
            column="continent",
            targets=[cnst.TABLE_AG_GRID_ID],
            selector=vm.Checklist(options=["Asia", "Oceania"]),
        ),
        vm.Filter(
            column="pop",
            targets=[cnst.TABLE_AG_GRID_ID],
            selector=vm.RangeSlider(step=1000000.0, min=1000000, max=10000000),
        ),
    ],
)
