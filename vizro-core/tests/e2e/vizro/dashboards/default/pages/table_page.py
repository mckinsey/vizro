import e2e.vizro.constants as cnst

import vizro.models as vm
import vizro.plotly.express as px
from vizro.tables import dash_data_table

gapminder = px.data.gapminder()

table_page = vm.Page(
    title=cnst.TABLE_PAGE,
    components=[
        vm.Container(
            title=cnst.TABLE_CONTAINER,
            components=[
                vm.Table(
                    description=cnst.TABLE_TOOLTIP_TEXT,
                    id=cnst.TABLE_ID,
                    title="Table Country",
                    figure=dash_data_table(
                        data_frame=gapminder,
                    ),
                )
            ],
        )
    ],
    controls=[
        vm.Filter(column="year", selector=vm.Dropdown(value=2007)),
        vm.Filter(
            column="continent",
            selector=vm.RadioItems(id=cnst.RADIOITEMS_TABLE_FILTER, options=["Europe", "Africa", "Americas"]),
        ),
        vm.Filter(
            column="continent",
            selector=vm.Checklist(id=cnst.CHECKLIST_TABLE_FILTER, options=["Asia", "Oceania"]),
        ),
        vm.Filter(
            column="pop",
            selector=vm.RangeSlider(id=cnst.RANGESLIDER_TABLE_FILTER, step=1000000.0, min=1000000, max=10000000),
        ),
    ],
)
