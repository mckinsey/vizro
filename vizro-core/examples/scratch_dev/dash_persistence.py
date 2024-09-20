import datetime
import dash
import plotly.express as px

from dash import Dash, html, dcc, Output, callback, clientside_callback, Input, State, set_props


# like dynamic data
def slow_load():
    print("running slow_load")
    return px.data.iris()#.sample(6)


common = [
    html.H1(id="dashboard_title", children="Dashboard"),
    html.Div(dcc.Link("Homepage", href="/")),
    html.Div(dcc.Link("Another page", href="/another-page")),
]


def make_page(content):
    return html.Div(
        [
            *common,
            html.P(datetime.datetime.now()),
            *content,
        ]
    )


# like build
def homepage(**kwargs):
    return make_page([html.H2("Homepage")])


# like page build
def another_page(**kwargs):
    return make_page(
        [
            dcc.Store(id="on_page_load_trigger_another_page", data="123"),
            html.H2("Another page"),

            # Filter
            html.Div(
                id="filter_container",
                children=[html.Div(id="filter")],
            ),

            # Grid
            html.Div(
                id="graph_container",
                children=[html.Div(id="graph")],
            ),
        ]
    )


def get_data(species):
    df = slow_load()
    return df[df["species"].isin(species)]


# This mechanism is not actually necessary in this example since can just let OPL run without this trigger removing
# prevent_initial_call=True from it.
clientside_callback(
    """
    function trigger_to_global_store(data) {
        return data;
    }
    """,
    Output("global_on_page_load_another_page_action_trigger", "data"),
    Input("on_page_load_trigger_another_page", "data"),
    prevent_initial_call=True,  # doesn't do anything - callback still runs
)


@callback(
    Output("graph_container", "children"),
    Output("filter_container", "children"),
    Input("global_on_page_load_another_page_action_trigger", "data"),
    State("filter", "value"),
    prevent_initial_call=True
)
# TODO - ANSWER -> It can't propagate persisted value to the on_page_load input
#  as it's an empty html.Div object created by page.build()...
def on_page_load(trigger, persisted_filter_value):
    print("running on_page_load")
    df = slow_load()

    categorical_filter_options = sorted(df["species"].unique().tolist())

    if not persisted_filter_value:
        categorical_filter_value = []
    else:
        categorical_filter_value = [value for value in persisted_filter_value if value in categorical_filter_options]

    categorical_filter_obj = dcc.Dropdown(
        id="filter",
        options=categorical_filter_options,
        value=categorical_filter_value,
        persistence=True,
        persistence_type="session",
        multi=True,
    )

    # set_props(component_id="categorical_filter_container", props={"children": categorical_filter_obj})
    df = df[df["species"].isin(categorical_filter_value)]

    graph_obj = dcc.Graph(
        id="graph",
        figure=px.scatter(df, x="sepal_length", y="sepal_width", color="species")
    )

    print("")
    return graph_obj, categorical_filter_obj


app = Dash(use_pages=True, pages_folder="", suppress_callback_exceptions=True)
dash.register_page("/", layout=homepage)
dash.register_page("another_page", layout=another_page)

app.layout = html.Div([dcc.Store("global_on_page_load_another_page_action_trigger"), dash.page_container])

if __name__ == "__main__":
    app.run(dev_tools_hot_reload=False)
