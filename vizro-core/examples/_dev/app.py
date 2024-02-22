import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid

df = px.data.gapminder()

cellStyle = {
    "styleConditions": [
        {
            "condition": "params.value < 1045",
            "style": {"backgroundColor": "#ff9222"},
        },
        {
            "condition": "params.value >= 1045 && params.value <= 4095",
            "style": {"backgroundColor": "#de9e75"},
        },
        {
            "condition": "params.value > 4095 && params.value <= 12695",
            "style": {"backgroundColor": "#aaa9ba"},
        },
        {
            "condition": "params.value > 12695",
            "style": {"backgroundColor": "#00b4ff"},
        },
    ]
}

columnDefs = [
    {"field": "country"},
    {"field": "continent"},
    {"field": "year"},
    {
        "field": "lifeExp",
        "valueFormatter": {"function": "d3.format('.1f')(params.value)"},
    },
    {
        "field": "gdpPercap",
        "valueFormatter": {"function": "d3.format('$,.1f')(params.value)"},
        "cellStyle": cellStyle,
    },
    {
        "field": "pop",
        "valueFormatter": {"function": "d3.format(',.0f')(params.value)"},
    },
]

page = vm.Page(
    title="Example of Modified Dash AG Grid",
    components=[
        vm.AgGrid(
            title="Modified Dash AG Grid",
            figure=dash_ag_grid(
                data_frame=df,
                columnDefs=columnDefs,
                defaultColDef={"resizable": False, "filter": False, "editable": True},
            ),
        )
    ],
)

dashboard = vm.Dashboard(pages=[page])

Vizro().build(dashboard).run()
