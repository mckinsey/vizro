import dash
from dash import html, dcc, Input, Output

app = dash.Dash(__name__)

app.layout = [
    dcc.Input(id="input-text"),
    html.Div(id="server-output"),
    html.Button("Click", id="btn"),
    html.Div(id="client-output"),
]


@app.callback(Output("server-output", "children"), Input("input-text", "value"), hidden=True)
def server_cb(value):
    return ""


app.clientside_callback(
    "function(n){return ''}", Output("client-output", "children"), Input("btn", "n_clicks"), hidden=True
)

if __name__ == "__main__":
    app.run(debug=True)
