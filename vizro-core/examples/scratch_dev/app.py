import datetime
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, Dash


# TODO-FOR-REVIEWER:
#  Reproduce bug A:
#    A.1. Go to http://127.0.0.1:8050/another-page?radio_items_id_value=3
#    A.2. Click "Homepage"
#    A.3. Click “Another page” -> value is set to 1 but should be 3
#  Reproduce bug B:
#    B.1. Go to http://127.0.0.1:8050/another-page?radio_items_id_value=3
#    B.2. Change value to 2
#    B.3. Click "Homepage"
#    B.4. Click “Another page” -> value is set to 1 but should be 2


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
