import datetime
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, Dash


common = [
    html.H1(children="Dashboard"),
    html.Div(dcc.Link("Homepage", href="/")),
    html.Div(dcc.Link("Another page", href="/another-page")),
]


def homepage(**kwargs):
    return html.H2("Homepage")


def another_page(radio_items_id_value=1):
    return html.Div(
        [
            html.H2("Another page"),
            dcc.RadioItems(
                id="radio_items_id",
                options=[1, 2, 3],
                value=int(radio_items_id_value),
                persistence=True,
                persistence_type="session",
            ),
        ]
    )


app = Dash(
    use_pages=True,
    pages_folder="",
    # suppress_callback_exceptions=True,
)

dash.register_page("/", layout=homepage)
dash.register_page("another-page", layout=another_page)

app.layout = [*common, dash.page_container]

if __name__ == "__main__":
    app.run(debug=True, dev_tools_hot_reload=False)
