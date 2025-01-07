"""****** Important! *******
If you run this app locally, un-comment line 127 to add the theme change components to the layout
"""

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Dash, Input, Output, callback, clientside_callback, dcc, html

df = px.data.gapminder()
years = df.year.unique()
continents = df.continent.unique()

# Test out local vizro-bootstrap file. Note: It takes a while after a commit for the updated file to be available
base = "https://cdn.jsdelivr.net/gh/mckinsey/vizro@tidy/add-bs-theme/vizro-core/src/vizro/static/css/"
vizro_bootstrap = base + "vizro-bootstrap.min.css"

app = Dash(
    __name__,
    external_stylesheets=[
        #  dbc.themes.BOOTSTRAP,
        vizro_bootstrap,
        dbc.icons.FONT_AWESOME,
    ],
)

header = html.H3("Theme Explorer Sample App", className="bg-primary p-2 mt-4")

grid = dag.AgGrid(
    id="grid",
    columnDefs=[{"field": i} for i in df.columns],
    rowData=df.to_dict("records"),
    defaultColDef={"flex": 1, "minWidth": 120, "sortable": True, "resizable": True, "filter": True},
    dashGridOptions={"rowSelection": "multiple"},
)

dropdown = html.Div(
    [
        dbc.Label("Select indicator (y-axis)"),
        dcc.Dropdown(
            ["gdpPercap", "lifeExp", "pop"],
            "pop",
            id="indicator",
            clearable=False,
        ),
    ],
    className="mb-4",
)

checklist = html.Div(
    [
        dbc.Label("Select Continents"),
        dbc.Checklist(
            id="continents",
            options=continents,
            value=continents,
            inline=True,
        ),
    ],
    className="mb-4",
)

slider = html.Div(
    [
        dbc.Label("Select Years"),
        dcc.RangeSlider(
            years[0],
            years[-1],
            5,
            id="years",
            marks=None,
            tooltip={"placement": "bottom", "always_visible": True},
            value=[years[2], years[-2]],
            className="p-0",
        ),
    ],
    className="mb-5",
)

toggle = dbc.Switch(id="switch", value=False, persistence=True, persistence_type="session")

theme_colors = [
    "primary",
    "secondary",
    "success",
    "warning",
    "danger",
    "info",
    "light",
    "dark",
    "link",
]

colors = html.Div([dbc.Button(f"{color}", color=f"{color}", size="sm") for color in theme_colors])
colors = html.Div(["Theme Colors:", colors], className="mt-2")

controls = dbc.Card([dropdown, checklist, slider, toggle])
tab1 = dbc.Tab([dcc.Graph(id="line-chart", figure=px.line())], label="Line Chart", className="p-4")
tab2 = dbc.Tab([dcc.Graph(id="scatter-chart", figure=px.scatter())], label="Scatter Chart", className="p-4")
tab3 = dbc.Tab([grid], label="Grid", className="p-4")
tabs = dbc.Card(dbc.Tabs([tab1, tab2, tab3]))

app.layout = html.Div(
    children=[header, dbc.Row([dbc.Col(controls, width=4), dbc.Col([tabs, colors], width=8)])],
)


@callback(
    Output("line-chart", "figure"),
    Output("scatter-chart", "figure"),
    Output("grid", "dashGridOptions"),
    Input("indicator", "value"),
    Input("continents", "value"),
    Input("years", "value"),
)
def update(indicator, continent, yrs):
    if continent == [] or indicator is None:
        return {}, {}, {}

    dff = df[df.year.between(yrs[0], yrs[1])]
    dff = dff[dff.continent.isin(continent)]

    fig = px.line(
        dff,
        x="year",
        y=indicator,
        color="continent",
        line_group="country",
    )

    fig_scatter = px.scatter(
        dff[dff.year == yrs[0]],
        x="gdpPercap",
        y="lifeExp",
        size="pop",
        color="continent",
        log_x=True,
        size_max=60,
    )

    grid_filter = (
        f"{continent}.includes(params.data.continent) && params.data.year >= {yrs[0]} && params.data.year <= {yrs[1]}"
    )
    dashGridOptions = {
        "isExternalFilterPresent": {"function": "true"},
        "doesExternalFilterPass": {"function": grid_filter},
    }
    return fig, fig_scatter, dashGridOptions


# updates the Bootstrap global light/dark color mode
clientside_callback(
    """
    switchOn => {
       document.documentElement.setAttribute('data-bs-theme', switchOn ? 'light' : 'dark');
       return window.dash_clientside.no_update
    }
    """,
    Output("switch", "id"),
    Input("switch", "value"),
)


if __name__ == "__main__":
    app.run_server(debug=True)
