"""Example to show dashboard configuration."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid

df = px.data.gapminder(datetimes=True)

page = vm.Page(
    title="Enhanced AG Grid",
    components=[
        vm.AgGrid(
            title="Dash AG Grid",
            figure=dash_ag_grid(
                data_frame=df,
                columnDefs=[
                    {"field": "country", "floatingFilter": True},
                    {"field": "continent", "floatingFilter": True},
                    {"field": "year"},
                    {"field": "lifeExp", "cellDataType": "numeric"},
                    {"field": "pop", "cellDataType": "numeric"},
                    {"field": "gdpPercap", "cellDataType": "euro"},
                ],
            ),
        ),
    ],
    controls=[vm.Filter(column="continent")],
)
dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
