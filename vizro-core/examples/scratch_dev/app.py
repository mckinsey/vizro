"""This is a test app to test the dashboard layout."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture
from vizro.actions import set_control
from vizro.tables import dash_ag_grid


df = px.data.iris()

import dash_bootstrap_components as dbc
from dash import hooks, html, clientside_callback, Output, Input, State

o = dbc.Offcanvas(
    id="vizro_logs_offcanvas",
    placement="bottom",
    scrollable=True,
    backdrop=False,
    is_open=False,
    children=html.Pre(id="vizro_logs", children=[]),
)

c = html.Button("Vizro logs", className="dash-debug-menu__button", id="open_vizro_logs")

c = c.to_plotly_json()
o = o.to_plotly_json()

hooks.devtool(namespace=c["namespace"], component_type=c["type"], props=c["props"])
hooks.devtool(namespace=o["namespace"], component_type=o["type"], props=o["props"])

clientside_callback(
    "function(_, is_open) { return !is_open }",
    Output("vizro_logs_offcanvas", "is_open"),
    Input("open_vizro_logs", "n_clicks"),
    State("vizro_logs_offcanvas", "is_open"),
)

import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm

df = px.data.iris()

page = vm.Page(
    title="My first dashboard",
    components=[
        vm.Graph(figure=px.scatter(df, x="sepal_length", y="petal_width", color="species")),
        vm.Graph(figure=px.histogram(df, x="sepal_width", color="species")),
    ],
    controls=[
        vm.Filter(column="species"),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
