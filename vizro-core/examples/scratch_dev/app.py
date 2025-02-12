"""Test app"""

from dash import Dash, html, clientside_callback, Output, Input
import dash_bootstrap_components as dbc
import vizro

app = Dash(__name__, external_stylesheets=[dbc.icons.FONT_AWESOME, vizro.bootstrap])

color_mode_switch = html.Span(
    [
        dbc.Label(className="fa fa-moon", html_for="switch"),
        dbc.Switch(id="switch", value=False, className="d-inline-block ms-1"),
        dbc.Label(className="fa fa-sun", html_for="switch"),
    ]
)

app.layout = dbc.Container(
    [
        html.H3(["Bootstrap Light Dark Color Modes Demo"], className="bg-primary p-2"),
        color_mode_switch,
    ]
)

clientside_callback(
    """
    (switchOn) => {
       switchOn
         ? document.documentElement.setAttribute('data-bs-theme', 'light')
         : document.documentElement.setAttribute('data-bs-theme', 'dark')
       return window.dash_clientside.no_update
    }
    """,
    Output("switch", "id"),
    Input("switch", "value"),
)

if __name__ == "__main__":
    app.run_server(debug=True)
