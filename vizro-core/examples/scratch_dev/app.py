import datetime
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, Dash


common = [
    html.H1(id="dashboard_title", children="Dashboard"),
    html.Div(dcc.Link("Homepage", href="/")),
    html.Div(dcc.Link("Another page", href="/another-page")),
]


def _page_build(content):
    page_build_obj = html.Div(
        [
            *common,
            html.P(datetime.datetime.now()),
            *content,
        ]
    )
    return page_build_obj


def homepage(**kwargs):
    return _page_build([
        html.H2("Homepage"),
        dbc.Button(
            id="button_id",
            children="Go to Another page (and set value=3)",
            href="/another-page?radio_items_id_value=3",
        ),
    ])


def another_page(radio_items_id_value=1, **kwargs):
    return _page_build([
        html.H2("Another page"),
        dcc.RadioItems(
            id="radio_items_id",
            options=[1, 2, 3],
            value=int(radio_items_id_value),
            persistence=True,
            persistence_type="session",
        )
    ])


app = Dash(
    use_pages=True,
    pages_folder="",
    suppress_callback_exceptions=True,
    # routing_callback_inputs={
    #     "radio_items_id_value": Input("radio_items_id", "value"),
    # },
)

dash.register_page("/", layout=homepage)
dash.register_page("another-page", layout=another_page)

app.layout = html.Div([
    dcc.Store("global_store"),
    dash.page_container,
    # dcc.RadioItems(id="radio_items_id", options=[], style={"display": "none"})
])

if __name__ == "__main__":
    app.run(debug=True, dev_tools_hot_reload=False)
