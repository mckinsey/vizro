import random
import dash
import datetime
import time
import plotly.express as px
import plotly.graph_objs as go

from dash import Dash, html, dcc, Output, callback, clientside_callback, Input, State, set_props


# like dynamic data
def slow_load():
    print("running slow_load")
    time.sleep(0.1)
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


# Like pre-build - doesn't get run again when reload page
# Not used currently - was used for static filter
initial_df = slow_load()
# options = sorted(initial_df["species"].unique().tolist())
sepal_length_min = float(initial_df["sepal_length"].min())
sepal_length_max = float(initial_df["sepal_length"].max())


def categorical_filter_build(options, value, selector, id_suffix=None, **kwargs):
    return selector(
        id=f'categorical_filter{id_suffix or ""}',
        options=options, value=value,
        persistence=True, persistence_type="session", **kwargs
    )


def numerical_filter_build(min_value, max_value, value=None, selector=dcc.RangeSlider, id_suffix=None, **kwargs):
    return selector(
        id=f'numerical_filter{id_suffix or ""}',
        min=min_value, max=max_value, step=0.1, value=value or [min_value, max_value],
        persistence=True, persistence_type="session", **kwargs
    )


# like page build
def another_page(**kwargs):
    return make_page(
        [
            dcc.Store(id="on_page_load_trigger_another_page"),
            html.H2("Another page"),

            # This does NOT work at all because id="filter" doesn't exist but is used as OPL callback State.
            # dcc.Loading(id="filter_container"),

            # fully dynamic version:
            # TODO-conclusion:
            # Does NOT persist for server (OPL input argument), although correctly persists on the UI.
            # The reason is that the dcc.Dropdown component is created as a result of on_page_load.
            # dcc.Loading(html.Div(html.Div(id="filter"), id="filter_container")),

            # static version:
            # TODO-conclusion:
            # Possible solution is to alter filter."options" from on_page_load. This would work, but it's not optimal.
            # dcc.Dropdown(id="filter", options=options, value=options, multi=True, persistence=True),

            # semi dynamic version:
            # TODO-conclusion:
            # Persists just first time for UI and server. The reason is that the dcc.Dropdown component is created twice per page refresh.
            dcc.Loading(
                categorical_filter_build(
                    options=["setosa", "versicolor", "virginica"], value=["setosa", "versicolor", "virginica"],
                    selector=dcc.Dropdown,
                    multi=True
                ),
                id="categorical_filter_container",
            ),
            # 2. Neither UI nor server persistence works
            # dcc.Loading(
            #     dcc.Dropdown(id="filter", options=options, multi=True, persistence=True, persistence_type="session"),
            #     id="filter_container"
            # ),
            # 3. Neither UI nor server persistence works
            # dcc.Loading(
            #     dcc.Dropdown(id="filter", persistence=True, persistence_type="session"),
            #     id="filter_container"
            # ),
            # 4. Same as "fully dynamic version"
            # dcc.Loading(
            #     html.Div(
            #         dcc.Dropdown(id="filter"),
            #         id="filter_container",
            #     )
            # ),

            # Numerical filter:
            # dcc.Loading(
            #     numerical_filter_build(
            #         min_value=sepal_length_min, max_value=sepal_length_max, selector=dcc.RangeSlider,
            #     ),
            #     id="numerical_filter_container",
            # ),


            dcc.RadioItems(id="parameter", options=["sepal_width", "sepal_length"], value="sepal_width", persistence=True, persistence_type="session"),
            dcc.Loading(dcc.Graph(id="graph1")),
            dcc.Loading(dcc.Graph(id="graph2")),
        ]
    )


def graph1_call(data_frame):
    return px.bar(data_frame, x="species", color="species")


def graph2_call(data_frame, x):
    return px.scatter(data_frame, x=x, y="petal_width", color="species")


# NOTE:
# You could do just update_filter to update options/value rather than replacing whole dcc.Dropdown object. Then would
# need to write it for rangeslider and dropdown etc. separately though. Probably easier to just replace whole object.
# This is consistent with how Graph, AgGrid etc. work.
# BUT controls are different from Graphs since you can set the pre-selected value that should be shown when
# user first visits page. Is this possible still with dynamic filter?
# QUESTION: Even though we replace the whole object, persistence=True still seems to work. How?
# TODO - answer: It doesn't work :(


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


# TODO: write something like get_modified_figures function to reduce repetition.


@callback(
    Output("graph1", "figure"),
    Output("graph2", "figure"),
    # Output("categorical_filter_container", "children"),
    # Output("numerical_filter_container", "children"),
    # Input("on_page_load_trigger_another_page", "data"),  # this is arbitrary since callback runs on page load
    # automatically. Just need to define some Input.
    Input("global_on_page_load_another_page_action_trigger", "data"),
    State("categorical_filter", "value"),
    State("parameter", "value"),
    # State("numerical_filter", "value"),
    prevent_initial_call=True
)
def on_page_load(data, species, x):
    # Ideally, OPL flow should look like this:
    #  1. Page.build() -> returns static layout (placeholder elements for dynamic components).
    #  2. Persistence is applied. -> So, filter values are the same as the last time the page was visited.
    #  3. OPL -> returns dynamic components based on the controls values (persisted)
    #     3.1. Load DFs (include DFP values here)
    #     3.2. Calculate new filter values:
    #         e.g. new_filter_values = [value for value in persisted_filter_value if value in new_filter_options]
    #         e.g. new_min = max(persisted_min, new_min); new_max = min(persisted_max, new_max)
    #     3.3. Apply filters on DFs
    #     3.4. Apply parameters on config
    #     3.5. Return dynamic components (Figures and dynamic controls)

    # Why actions are better than dash.callback here?
    #   1. They solve the circular dependency problem of the full graph.
    #   2. They are explicit which means they can be configured in any way users want. There's no undesired behavior.

    print("running on_page_load")
    df = slow_load()

    # filter_options -> always calculate.
    categorical_filter_options = sorted(df["species"].unique().tolist())
    # For multi=True:
    categorical_filter_value = [value for value in species if value in categorical_filter_options]
    # For multi=False:
    # categorical_filter_value = species if species in categorical_filter_options else None
    categorical_filter_obj = categorical_filter_build(options=categorical_filter_options, value=categorical_filter_value, selector=dcc.Dropdown, multi=True)

    set_props(component_id="categorical_filter_container", props={"children": categorical_filter_obj})
    # More about set_props:
    #   -> https://dash.plotly.com/advanced-callbacks#setting-properties-directly
    #   -> https://community.plotly.com/t/dash-2-17-0-released-callback-updates-with-set-props-no-output-callbacks-layout-as-list-dcc-loading-trace-zorder/84343
    # Limitations:
    #   1. Component properties updated using set_props won't appear in the callback graph for debugging.
    #      - This is not a problem because our graph debugging is already unreadable. :D
    #   2. Component properties updated using set_props won't appear as loading when they are wrapped with a `dcc.Loading` component.
    #      - Potential solution. Set controls as dash.Output and then use set_props to update them + dash.no_update as a return value for them.
    #   3. set_props doesn't validate the id or property names provided, so no error will be displayed if they contain typos. This can make apps that use set_props harder to debug.
    #      - That's okay since it's internal Vizro stuff and shouldn't affect user.
    #   4. Using set_props with chained callbacks may lead to unexpected results.
    #      - It even behaves better because it doesn't trigger the "do_filter" callback.
    # Open questions:
    #   1. Is there any concern about different filter selectors? -> No. (I haven't tested the DatePicker it yet.)
    #   2. Can we handle if filter selector changes dynamically? -> Potentially, (I haven't tested it yet.)
    #   3. Is there a bug with set_props or with dash.Output?!

    # sepal_length numerical filter
    # numerical_filter_min = float(df["sepal_length"].min())
    # numerical_filter_max = float(df["sepal_length"].max())
    # For dcc.Slider
    # numerical_filter_value = sepal_length_range if numerical_filter_min < sepal_length_range < numerical_filter_max else numerical_filter_min
    # For dcc.RangeSlider
    # numerical_filter_value = [max(numerical_filter_min, sepal_length_range[0]), min(numerical_filter_max, sepal_length_range[1])]
    # numerical_filter_obj = numerical_filter_build(numerical_filter_min, numerical_filter_max, numerical_filter_value, dcc.RangeSlider)
    # set_props(component_id="numerical_filter_container", props={"children": numerical_filter_obj})

    # PROBLEM: How to achieve all of these:
    # * get correct selected value passed into graph calls -> set_props is a solution
    # * populate filter with right values for user on first page load -> set_props is a solution
    # * update filter options on page load -> set_props is a solution
    # * persist filter values on page change -> set_props is a solution
    df = df[df["species"].isin(categorical_filter_value)]
    # df = df[(df["sepal_length"] >= numerical_filter_value[0]) & (df["sepal_length"] <= numerical_filter_value[1])]

    print("")
    return graph1_call(df), graph2_call(df, x)


@callback(
    Output("graph1", "figure", allow_duplicate=True),
    Output("graph2", "figure", allow_duplicate=True),
    Input("categorical_filter", "value"),
    State("parameter", "value"),
    prevent_initial_call=True,
)
def do_filter(species, x):
    print("running do_filter")

    # This also works - filter is calculated on filter value select:
    # It also makes that filter/df1/df2 are calculated based on the same data. Should we enable that?
    # df = slow_load()
    # filter_options = df["species"].unique()
    # filter_value = [value for value in species if value in filter_options]
    # filter_obj = filter_call(filter_options, filter_value)
    # df1 = df2 = df[df["species"].isin(filter_value)]
    # set_props(component_id="filter_container", props={"children": filter_obj})

    df1 = get_data(species)
    df2 = get_data(species)
    print("")
    return graph1_call(df1), graph2_call(df2, x)


@callback(
    Output("graph2", "figure", allow_duplicate=True),
    Input("parameter", "value"),
    State("categorical_filter", "value"),
    prevent_initial_call=True,
)
def do_parameter(x, species):
    print("running do_parameter")
    df1 = get_data(species)
    print("")
    return graph2_call(df1, x)


app = Dash(use_pages=True, pages_folder="", suppress_callback_exceptions=True)
dash.register_page("/", layout=homepage)
dash.register_page("another_page", layout=another_page)

app.layout = html.Div([dcc.Store("global_on_page_load_another_page_action_trigger"), dash.page_container])

##### NEXT STEPS FOR PETAR

# How to update dynamic filter?
# Options:
#  1. on_page_load_controls and then on_page_load_components sequentially. Need to figure out how to get components
#  into loading state to begin with - set as loading build and then change back in OPL callback? Means two callbacks.
#  2. on_page_load_controls and then on_page_load_components in parallel. NO, bad when caching
#  3. on_page_load_everything. THIS IS THE ONE WE PREFER.
# Can't have on_page_load_controls trigger regular "apply filter" etc. callbacks as could lead to many of them in
# parallel.

# So need to make sure that either method 1 or 3 doesn't trigger regular callbacks. Not sure
# how to achieve this...
# Could put manual no_update in those regular callbacks but is not nice.
# Could actually just do on_page_load_controls and then use all regular callbacks in parallel - so long as caching
# turned on then on_page_load_controls will have warmed it up so then no problem with regular callbacks.
# But still not good because regular callbacks will override same output graph multiple times.


# Maybe actually need on_page_load_controls to trigger regular filters in general? And just not have too many of them.

# persistence still works
# changing page now does on_page_load which then triggers do_filter
# so effectively running do_filter twice
# How can we avoid this?

# Consider actions loop and when one callback should trigger another etc.

# How does persistence work?
# How does triggering callbacks work in vizro?
# How *should* triggering callbacks work in vizro? Can we align it more with Dash?
# How to handle filter options persistence and updating etc.?
# How to avoid the regular filters being triggered after on_page_load runs?
# IMPORTANT: also consider parametrised data case.

if __name__ == "__main__":
    app.run(dev_tools_hot_reload=False)
