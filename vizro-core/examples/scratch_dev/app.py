import datetime
import dash
import dash_bootstrap_components as dbc

from urllib.parse import urlencode, parse_qs
from dash import html, dcc, callback, Input, Output, Dash, no_update, ctx
from dash.exceptions import PreventUpdate


# TODO-FOR-REVIEWER:
#  Bug exists on poc/drill-through-with-persistence branch
#  Reproduce bug A:
#    A.1. Go to http://127.0.0.1:8050/another-page?radio_items_id=3
#    A.2. Click "Homepage"
#    A.3. Click “Another page” -> value is set to 1 but should be 3
#  Reproduce bug B:
#    B.1. Go to http://127.0.0.1:8050/another-page?radio_items_id=3
#    B.2. Change value to 2
#    B.3. Click "Homepage"
#    B.4. Click “Another page” -> value is set to 1 but should be 2
#  IMPORTANT:
#   The bug is fixed in poc/dash-url-query-params-overwrite-persistence when new dash with persistence bugfix is used.

common = [
    html.H1(children="Dashboard"),
    html.Div(dcc.Link("Homepage", href="/")),
    html.Div(dcc.Link("Another page", href="/another-page")),
    html.Div(dcc.Link("Another page with ?radio_items_id=3", href="/another-page?radio_items_id=3")),
]


def homepage(**kwargs):
    return html.H2("Homepage")


def another_page(**kwargs):
    return html.Div(
        [
            html.H2("Another page"),
            dcc.RadioItems(
                id="radio_items_id",
                options=[1, 2, 3],
                value=1,
                persistence=True,
                persistence_type="session",
            ),
            dcc.Location(id="url", refresh="callback-nav"),
        ]
    )


# Keep controls and URL query params in sync
@callback(
    Output("url", "search"),
    Output("radio_items_id", "value"),
    Input("url", "search"),
    Input("radio_items_id", "value",),
)
def sync_radio_items_id(url_search, radio_items_value):
    radio_items_value = str(radio_items_value)

    query_params = parse_qs(url_search.lstrip("?"))
    url_value = query_params.get("radio_items_id", [None])[0]

    # TODO-NOW: Fix calling this callback twice
    if url_value == radio_items_value:
        raise PreventUpdate

    triggered_id = ctx.triggered_id

    if triggered_id == "url" and url_value:
        # URL changed → update radio item
        new_value = url_value if url_value is not None else 1
        return no_update, int(new_value)
    else:
        # Radio item changed → update URL
        query_params["radio_items_id"] = [radio_items_value]
        new_search = "?" + urlencode(query_params, doseq=True)
        return new_search, no_update


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
