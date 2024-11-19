import dash
import datetime
import time
import yaml
import pandas as pd
import plotly.express as px

from dash import Dash, html, dcc, Output, callback, clientside_callback, Input, State, set_props
import dash_mantine_components as dmc
from time import sleep

# TODO-TEST: How to test this?
#  =====================================================================
#  *** ATTENTION: THIS IS THE ONLY VARIABLE YOU NEED TO SET ***
#  Set CONTROL_SELECTOR to test different control types
#  Choose between: dcc.Dropdown, dcc.Checklist, dcc.RadioItems, dcc.Slider, dcc.RangeSlider
#  For example: CONTROL_SELECTOR = dcc.RadioItems
#  Optionally, choose between IS_DROPDOWN_MULTI = True or False for dcc.Dropdown selector.
#  =====================================================================
CONTROL_SELECTOR = dcc.Checklist

# IS_DROPDOWN_MULTI must be set to True or False for dcc.Dropdown selector.
IS_DROPDOWN_MULTI = True
# =====================================================================


# Set MULTI based on CONTROL_SELECTOR and IS_DROPDOWN_MULTI
if CONTROL_SELECTOR in {dcc.Checklist, dcc.RangeSlider}:
    MULTI = True
elif CONTROL_SELECTOR in {dcc.Slider, dcc.RadioItems}:
    MULTI = False
elif CONTROL_SELECTOR == dcc.Dropdown:
    if IS_DROPDOWN_MULTI not in [False, True]:
        raise ValueError("IS_DROPDOWN_MULTI must be set to True or False for dcc.Dropdown selector.")
    MULTI = IS_DROPDOWN_MULTI
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

# This is automatically calculated based on CONTROL_SELECTOR
LOADING_DATA_PREFILTER_COLUMN = None

if CONTROL_SELECTOR in SELECTOR_TYPE["categorical"]:
    LOADING_DATA_PREFILTER_COLUMN = "species"
elif CONTROL_SELECTOR in SELECTOR_TYPE["numerical"]:
    LOADING_DATA_PREFILTER_COLUMN = "sepal_length"


# like dynamic data
def slow_load():
    print("running slow_load")
    sleep(0.1)

    # Load the full iris dataset
    df = px.data.iris()
    df["date_column"] = pd.date_range(start=pd.to_datetime("2024-01-01"), periods=len(df), freq="D")

    with open("data.yaml", "r") as file:
        data = yaml.safe_load(file)
        data = data or {}

    filter_column = LOADING_DATA_PREFILTER_COLUMN
    if filter_column == "species":
        final_df = pd.concat(
            objs=[
                df[df[filter_column] == "setosa"].head(data.get("setosa", 0)),
                df[df[filter_column] == "versicolor"].head(data.get("versicolor", 0)),
                df[df[filter_column] == "virginica"].head(data.get("virginica", 0)),
            ],
            ignore_index=True,
        )
    elif filter_column == "sepal_length":
        final_df = df[df[filter_column].between(data.get("min"), data.get("max"), inclusive="both")]
    elif filter_column == "date_column":
        date_min = pd.to_datetime(data.get("date_min"))
        date_max = pd.to_datetime(data.get("date_max"))
        final_df = df[df[filter_column].between(date_min, date_max, inclusive="both")]
    else:
        raise ValueError("Invalid FILTER_COLUMN")

    return final_df


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


# TODO-TEST: You can hardcode these values for testing purposes. They represent initial options/min/max/value
#  for the filter that are created in and sent from page.build() every time page is refreshed.
pre_build_options, pre_build_categorical_value = categorical_filter_pre_build()
pre_build_min, pre_build_max, pre_build_numerical_value = numerical_filter_pre_build()


# Like filter build - gets run every time page is loaded
def categorical_filter_build(options=None):
    kwargs = {}
    if CONTROL_SELECTOR == dcc.Dropdown:
        kwargs["multi"] = MULTI

    return CONTROL_SELECTOR(
        id=f'filter',
        options=options or pre_build_options,
        value=pre_build_categorical_value,
        persistence=True,
        persistence_type="session",
        **kwargs
    )


def numerical_filter_build(min_value=None, max_value=None):
    return CONTROL_SELECTOR(
        id=f'filter',
        min=min_value or pre_build_min,
        max=max_value or pre_build_max,
        value=pre_build_numerical_value,
        step=0.1,
        persistence=True,
        persistence_type="session",
    )


# --- Pages ---
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


# homepage build
def homepage(**kwargs):
    return _page_build([html.H2("Homepage")])


# Like another-page build
def another_page(**kwargs):
    def _get_initial_page_build_object():
        if CONTROL_SELECTOR == dcc.Dropdown:
            # A hack explained in on_page_load To-do "Limitations" section.
            return dmc.DateRangePicker(
                id='filter',
                value=pre_build_categorical_value,
                persistence=True,
                persistence_type="session",
            )
        elif CONTROL_SELECTOR in SELECTOR_TYPE["categorical"]:
            return categorical_filter_build()
        elif CONTROL_SELECTOR in SELECTOR_TYPE["numerical"]:
            return numerical_filter_build()
        else:
            raise ValueError("Invalid CONTROL_SELECTOR.")

    return _page_build(
        [
            dcc.Store(id="on_page_load_trigger_another_page"),
            html.H2("Another page"),

            # # This does not work because id="filter" doesn't exist but is used as OPL callback State.
            # dcc.Loading(id="filter_container"),

            # # This does not work because OPL filter input ("value") is missing, but is used for filtering dfs.
            # html.Div(
            #     html.Div(id="filter"),
            #     id="filter_container",
            # ),

            # # This does not work because setting the different "value" clears the session persistence storage
            # dcc.Dropdown(id="filter", options=options, value=options, multi=True, persistence=True),

            # # This works because filter "value" is always set to the same value in the page_build
            # # and persistence is applied properly before the OPL.
            html.Div(
                _get_initial_page_build_object(),
                id="filter_container",
            ),

            html.Br(),
            dcc.RadioItems(id="parameter", options=["sepal_width", "sepal_length"], value="sepal_width", persistence=True, persistence_type="session"),
            dcc.Loading(dcc.Graph(id="graph1")),
            dcc.Loading(dcc.Graph(id="graph2")),
        ]
    )


def graph1_build(data_frame):
    return px.bar(data_frame, x="species", color="species")


def graph2_build(data_frame, x):
    return px.scatter(data_frame, x=x, y="petal_width", color="species")


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
    #  3. OPL -> returns dynamic components based on the persisted controls values
    #     3.1. Load DFs (include DFP values here)
    #     3.2. Calculate new filter values:
    #         e.g. options = persisted_current_value + new_options
    #         e.g. new_min = min(persisted_min, new_min); new_max = max(persisted_max, new_max)
    #     3.3. Apply filters on DFs
    #     3.4. Apply parameters on config
    #     3.5. Return dynamic components (Figures and dynamic controls)

    # Why actions are better than dash.callback here?
    #   1. They solve the circular dependency problem of the full graph (filter_1 -> graph -> filter_2 -> filter_1).
    #      graph -> filter_2 (filter_interaction over the controls); filter_2 -> filter_1 (cascading filters).
    #   2. They are explicit which means they can be configured in any way users want. There's no undesired behavior.

    # TODO: Last solution found -> hence put in highlighted TODO:
    #  1. page.build() -> returns:
    #    1.1. html.Div(html.Div(id="filter"), id="filter_container")
    #      * Does not work because we need persisted filter input value in OPL, so we can filter figures data_frame. *
    #    1.2. html.Div(dcc.Dropdown(id="filter", ...), id="filter_container")
    #      * It works! :D *
    #  2. OPL -> Manipulations with filter and options:
    #    2.1. Recalculate options.
    #    2.2. Filter figures data_frame with recalculated value.
    #    2.3. Create a new filter object with recalculated options and original value.
    #  Limitations:
    #    1. do_filter is triggered automatically after OPL.
    #      This shouldn't be the issue since actions loop controls it.
    #    2. Component persistence updating works slightly different for dcc.Dropdown than for other selector components.
    #      Persistence for Dropdown is set even when the Dropdown is returned as a new object from page_build or OPL.
    #      In persistence.js -> LN:309 "recordUiEdit" function is triggered when dropdown is returned from the server.
    #      It causes storage.SetItem() to be triggered which mess-ups the persistence for the Dropdown.
    #      This is probably dash bug because Dropdown is handled a lot with async which probably causes that returned
    #      Dropdown from the page_build or OPL triggers the "recordUiEdit" which should not trigger.
    #      ** Problem is solved by returning dmc.DateRangePicker instead of dcc.Dropdown from page.build. **
    #    3. We should stick with new_options = current_value + new_options for all our selectors to keep in sync
    #      persistence stored values with the UI selected values.
    #    4. set_props also could be used but we avoid this due to lack of documentation and potential bugs.
    #     # Usage:
    #     #   set_props(component_id="filter_container", props={"children": new_filter_obj})
    #     # More about set_props:
    #     #   -> https://dash.plotly.com/advanced-callbacks#setting-properties-directly
    print("running on_page_load")
    df = slow_load()

    # --- Calculate categorical filter ---
    if CONTROL_SELECTOR in SELECTOR_TYPE["categorical"]:
        # Changing current_value format for easier handling
        persisted_filter_value = persisted_filter_value if isinstance(persisted_filter_value, list) else [persisted_filter_value]

        # Fetching new options
        categorical_filter_options = sorted(df["species"].unique().tolist())

        # new_options = current_value + new_options
        categorical_filter_options = sorted(list(set(categorical_filter_options + persisted_filter_value)))

        new_filter_obj = categorical_filter_build(options=categorical_filter_options)

        # --- Filtering data: ---
        df = df[df["species"].isin(persisted_filter_value)]

    # --- Calculate numerical filter ---
    if CONTROL_SELECTOR in SELECTOR_TYPE["numerical"]:
        persisted_filter_value = persisted_filter_value if isinstance(persisted_filter_value, list) else [persisted_filter_value, persisted_filter_value]

        numerical_filter_min = float(df["sepal_length"].min())
        numerical_filter_max = float(df["sepal_length"].max())

        numerical_filter_min = min(numerical_filter_min, persisted_filter_value[0])
        numerical_filter_max = max(numerical_filter_max, persisted_filter_value[1])

        new_filter_obj = numerical_filter_build(min_value=numerical_filter_min, max_value=numerical_filter_max)

        # --- Filtering data: ---
        df = df[(df["sepal_length"] >= persisted_filter_value[0]) & (df["sepal_length"] <= persisted_filter_value[1])]

    print("")
    return graph1_build(df), graph2_build(df, x), new_filter_obj


# TODO-DEV: You can enable filtering by uncommenting the code below, but do_filter could be trigger from OPL.
#  There's no similar problems with when it's called in the Vizro app due to action loop breaking mechanism.
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
#     return graph1_build(df1), graph2_build(df2, x)
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


if __name__ == "__main__":
    app.run(debug=True, dev_tools_hot_reload=False)
