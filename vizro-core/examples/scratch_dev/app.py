import dash
import datetime
import time
import plotly.express as px

from dash import Dash, html, dcc, Output, callback, clientside_callback, Input, State, set_props


# TODO: How to test this?
#  =====================================================================
#  *** ATTENTION: THIS IS THE ONLY VARIABLE YOU NEED TO SET ***
#  Set CONTROL_SELECTOR to test different control types
#  Choose between: dcc.Dropdown, dcc.Checklist, dcc.RadioItems, dcc.Slider, dcc.RangeSlider
#  For example: CONTROL_SELECTOR = dcc.RadioItems
#  =====================================================================
CONTROL_SELECTOR = None
# MULTI must be set to True or False for dcc.Dropdown selector only, otherwise MULTI will be automatically calculated.
MULTI = None
# =====================================================================


# Set MULTI based on CONTROL_SELECTOR
if CONTROL_SELECTOR in {dcc.Checklist, dcc.RangeSlider}:
    MULTI = True
elif CONTROL_SELECTOR in {dcc.Slider, dcc.RadioItems}:
    MULTI = False
elif CONTROL_SELECTOR == dcc.Dropdown:
    if MULTI not in [False, True]:
        raise ValueError("MULTI must be set to True or False for dcc.Dropdown selector.")
else:
    raise ValueError(
        "Invalid CONTROL_SELECTOR. Must be one of: "
        "dcc.Dropdown, dcc.Checklist, dcc.RadioItems, dcc.Slider, or dcc.RangeSlider."
    )


# Hardcoded global variable.
SELECTOR_TYPE = {
    "categorical": [dcc.Dropdown, dcc.Checklist, dcc.RadioItems],
    "numerical": [dcc.Slider, dcc.RangeSlider],
}


# like dynamic data
def slow_load():
    print("running slow_load")
    time.sleep(0.1)
    return px.data.iris().sample(6)


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
def categorical_filter_pre_build():
    df = slow_load()
    options = sorted(df["species"].unique().tolist())
    return options, options if MULTI else options[0]


def numerical_filter_pre_build():
    df = slow_load()
    _min = float(df["sepal_length"].min())
    _max = float(df["sepal_length"].max())
    return _min, _max, [_min, _max] if MULTI else _min


pre_build_options, pre_build_categorical_value = categorical_filter_pre_build()
pre_build_min, pre_build_max, pre_build_numerical_value = numerical_filter_pre_build()


# Like build - gets run every time page is loaded
def categorical_filter_build(options=None, value=None, **kwargs):
    if CONTROL_SELECTOR == dcc.Dropdown:
        kwargs["multi"] = MULTI

    return CONTROL_SELECTOR(
        id=f'filter',
        options=options or pre_build_options,
        value=value or pre_build_categorical_value,
        persistence=True,
        persistence_type="session",
        **kwargs
    )


def numerical_filter_build(min_value=None, max_value=None, value=None, **kwargs):
    return CONTROL_SELECTOR(
        id=f'filter',
        min=min_value or pre_build_min,
        max=max_value or pre_build_max,
        value=value or pre_build_numerical_value,
        step=0.1,
        persistence=True,
        persistence_type="session",
        **kwargs
    )


# like page build
def another_page(**kwargs):
    return make_page(
        [
            dcc.Store(id="on_page_load_trigger_another_page"),
            html.H2("Another page"),

            # # This does NOT work because id="filter" doesn't exist but is used as OPL callback State.
            # dcc.Loading(id="filter_container"),

            # # Possible solution is to alter filter.options from on_page_load. This would work, but it's not optimal.
            # dcc.Dropdown(id="filter", options=options, value=options, multi=True, persistence=True),

            # TODO-DEV-TEST: Select a control.
            # # Working example of categorical filter
            # # Outer container can be changed with dcc.Loading.
            html.Div(
                categorical_filter_build() if CONTROL_SELECTOR in SELECTOR_TYPE["categorical"] else numerical_filter_build(),
                id="filter_container",
            ),

            # # Working example of numerical filter:
            # # Outer container can be changed with dcc.Loading.
            # html.Div(
            #     numerical_filter_build(),
            #     id="filter_container",
            # ),

            # # Does not work because OPL filter input is missing, but it's used for filtering figures data_frame.
            # html.Div(
            #     html.Div(id="filter"),
            #     id="filter_container",
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
# user first visits page. Is this possible still with dynamic filter? -> YES


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
    output=[
        Output("graph1", "figure"),
        Output("graph2", "figure"),
        Output("filter_container", "children"),
    ],
    inputs=[
        Input("global_on_page_load_another_page_action_trigger", "data"),

        State("filter", "value"),
        State("parameter", "value"),
    ],
    prevent_initial_call=True
)
def on_page_load(data, persisted_filter_value, x):
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

    # TODO: Last solution found -> hence put in highlighted TODO:
    #  1. page.build() -> returns:
    #    1.1. html.Div(html.Div(id="filter"), id="filter_container")
    #      * Does not work because we need persisted filter input value in OPL, so we can filter figures data_frame. *
    #    1.2. html.Div(dcc.Dropdown(id="filter", ...), id="filter_container")
    #      * It works! :D *
    #  2. OPL -> Manipulations with filter and options:
    #    2.1. Recalculate options.
    #    2.2. Recalculated value. (persisted_filter_value that exists in recalculated options)
    #    2.3. Filter figures data_frame with recalculated value.
    #    2.4. Create a new filter object with recalculated options and original value.
    #  Limitations:
    #    1. do_filter is triggered automatically after OPL.
    #      This shouldn't be the issue since actions loop controls it.
    #    2. Component persistence updating works slightly different for dcc.Dropdown than for other selector components.
    #      It changes its persistence even if OPL returns the different options. For other selector components,
    #      persistence is changed only if user manually change the value. This should be totally fine.
    #      Is it a bug on the dash side?
    # --- (A.M.): How to achieve all of these: ---
    # * get correct selected value passed into graph calls -> Works with this solution.
    # * populate filter with right values for user on first page load -> Works with this solution.
    # * update filter options on page load -> Works with this solution.
    # * persist filter values on page change -> Works with this solution.

    print("running on_page_load")
    df = slow_load()

    # --- Calculate categorical filter ---
    if CONTROL_SELECTOR in SELECTOR_TYPE["categorical"]:
        categorical_filter_options = sorted(df["species"].unique().tolist())
        if MULTI:
            categorical_filter_value = [value for value in persisted_filter_value if value in categorical_filter_options]
        else:
            categorical_filter_value = persisted_filter_value if persisted_filter_value in categorical_filter_options else None
        new_filter_obj = categorical_filter_build(options=categorical_filter_options)

        # --- Filtering data: ---
        if MULTI:
            df = df[df["species"].isin(categorical_filter_value)]
        else:
            df = df[df["species"].isin([categorical_filter_value])]

    # --- set_props ---
    # set_props(component_id="filter_container", props={"children": new_filter_obj})
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

    # --- Calculate numerical filter ---
    if CONTROL_SELECTOR in SELECTOR_TYPE["numerical"]:
        numerical_filter_min = float(df["sepal_length"].min())
        numerical_filter_max = float(df["sepal_length"].max())
        if MULTI:
            numerical_filter_value = [max(numerical_filter_min, persisted_filter_value[0]), min(numerical_filter_max, persisted_filter_value[1])]
        else:
            numerical_filter_value = persisted_filter_value if numerical_filter_min < persisted_filter_value < numerical_filter_max else numerical_filter_min
        new_filter_obj = numerical_filter_build(min_value=numerical_filter_min, max_value=numerical_filter_max)
        # set_props(component_id="numerical_filter_container", props={"children": new_filter_obj})

        # --- Filtering data: ---
        if MULTI:
            df = df[(df["sepal_length"] >= numerical_filter_value[0]) & (df["sepal_length"] <= numerical_filter_value[1])]
        else:
            df = df[(df["sepal_length"] == numerical_filter_value)]

    print("")
    return graph1_call(df), graph2_call(df, x), new_filter_obj


# @callback(
#     Output("graph1", "figure", allow_duplicate=True),
#     Output("graph2", "figure", allow_duplicate=True),
#     Input("filter", "value"),
#     State("parameter", "value"),
#     prevent_initial_call=True,
# )
# def do_filter(species, x):
#     print("running do_filter")
#
#     # This also works - filter is calculated on filter value select:
#     # It also makes that filter/df1/df2 are calculated based on the same data. Should we enable that?
#     # df = slow_load()
#     # filter_options = df["species"].unique()
#     # filter_value = [value for value in species if value in filter_options]
#     # filter_obj = filter_call(filter_options, filter_value)
#     # df1 = df2 = df[df["species"].isin(filter_value)]
#     # set_props(component_id="filter_container", props={"children": filter_obj})
#
#     df1 = get_data(species)
#     df2 = get_data(species)
#     print("")
#     return graph1_call(df1), graph2_call(df2, x)
#
#
# @callback(
#     Output("graph2", "figure", allow_duplicate=True),
#     Input("parameter", "value"),
#     State("filter", "value"),
#     prevent_initial_call=True,
# )
# def do_parameter(x, species):
#     print("running do_parameter")
#     df1 = get_data(species)
#     print("")
#     return graph2_call(df1, x)


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
