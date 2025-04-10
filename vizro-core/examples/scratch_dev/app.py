import datetime
import time
from typing import Annotated, Any, Literal, Optional

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from dash import Input, Output, State, callback, dcc, html
from dash_ag_grid import AgGrid
from flask_caching import Cache
from pydantic import AfterValidator, BaseModel, Field
from pydantic.functional_serializers import PlainSerializer
from vizro import Vizro
from vizro.actions import export_data, filter_interaction
from vizro.managers import data_manager
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._components.form._text_area import TextArea
from vizro.models._components.form._user_input import UserInput
from vizro.models._models_utils import _log_call
from vizro.models.types import ActionType, capture
from vizro.tables import dash_ag_grid
from vizro.tables._utils import _set_defaults_nested

df_gapminder = px.data.gapminder().query("year == 2007")

page_1 = vm.Page(
    title="Built in actions",
    layout=dict(grid=[[0, 1], [2, 3]]),
    components=[
        # vm.Button(
        #     text="asdf",
        #     actions=[filter_interaction(targets=["scatter_relation_2007"])],
        #     # actions=[vm.Action(function=filter_interaction(targets=["scatter_relation_2007"]))],  # CHECK
        # ),
        vm.Graph(
            figure=px.box(
                df_gapminder,
                x="continent",
                y="lifeExp",
                color="continent",
                custom_data=["continent"],
            ),
            actions=[filter_interaction(targets=["scatter_relation_2007"])],
            # actions=[vm.Action(function=filter_interaction(targets=["scatter_relation_2007"]))],  # CHECK
        ),
        vm.Graph(
            id="scatter_relation_2007",
            figure=px.scatter(
                df_gapminder,
                x="gdpPercap",
                y="lifeExp",
                size="pop",
                color="continent",
            ),
        ),
        vm.Button(
            id="button",
            text="Export data to CSV",
            # actions=[export_data(targets=["scatter_relation_2007"], runtime_arg="button.n_clicks")],
            # actions=[vm.Action(function=export_data(targets=["scatter_relation_2007"], runtime_arg="button.n_clicks"))],
            # CHECK
        ),
        vm.Button(
            id="button2",
            text="Export data to Excel",
            # actions=[
            #     export_data(targets=["scatter_relation_2007"], file_format="xlsx", runtime_arg="button2.n_clicks")
            # ],
            # actions=[
            #     vm.Action(
            #         function=export_data(
            #             targets=["scatter_relation_2007"],
            #             runtime_arg="button2.n_clicks",
            #             file_format="xlsx"
            #         )
            #     )
            # ],
            # CHECK
        ),
    ],
    controls=[
        vm.Filter(column="continent"),
        vm.Parameter(
            targets=["scatter_relation_2007.color"],
            selector=vm.RadioItems(options=["continent", "pop"]),
        ),
    ],
)


@capture("action")
# To test legacy=True
# def my_custom_action(points_data, _controls=None):
def my_custom_action(points_data, _controls):
    """Custom action."""
    clicked_point = points_data["points"][0]
    x, y = clicked_point["x"], clicked_point["y"]
    card_1_text = f"Clicked point has sepal length {x}, petal width {y}."
    card_2_text = f"Controls are `{_controls}`"
    return card_1_text, card_2_text


from typing import Annotated, Literal

from vizro.actions._abstract_action import _AbstractAction


class f(_AbstractAction):
    type: Literal["f"] = "f"
    points_data: str
    swap: bool = False

    def function(self, points_data, _controls):
        """Custom action."""
        clicked_point = points_data["points"][0]
        x, y = clicked_point["x"], clicked_point["y"]
        card_1_text = f"Clicked point has sepal length {x}, petal width {y}."
        card_2_text = f"_Controls are `{_controls}`"
        return card_1_text, card_2_text

    @property
    def outputs(self):
        return (
            ["my_card_2.children", "my_card_1.children"] if self.swap else ["my_card_1.children", "my_card_2.children"]
        )


from pydantic import Tag
from vizro.models._action._actions_chain import ActionsChain

f = Annotated[f, Tag("f")]

vm.Graph.add_type("actions", f)
ActionsChain.add_type("actions", f)

# @capture("action")
# def my_custom_action():
#     """Custom action."""
#     card_1_text = card_2_text = str(datetime.datetime.now().time())
#     return card_1_text, card_2_text

# CHECK: current docs examples
df = px.data.iris()

page_2 = vm.Page(
    title="Example of a custom action with UI inputs and outputs",
    layout=vm.Layout(
        grid=[
            [0, 0],
            [0, 0],
            [0, 0],
            [1, 2],
        ],
        row_gap="25px",
    ),
    components=[
        vm.Graph(
            id="scatter_chart",
            figure=px.scatter(df, x="sepal_length", y="petal_width", color="species", custom_data=["species"]),
            actions=[
                # vm.Action(
                #     function=my_custom_action("scatter_chart.clickData"),
                #     # CHECK: make sure user-specified argument continues to take precedence
                #     #     # function=my_custom_action("scatter_chart.clickData", controls="my_card_1.children"),
                #     #     # CHECK: test to make sure this old way continues to work
                #     #     # function=my_custom_action(),
                #     #     # function=my_custom_action(t=4),
                #     #     # inputs=["scatter_chart.clickData"],
                #     outputs=["my_card_1.children", "my_card_2.children"],
                # ),
                f(swap=True, points_data="scatter_chart.clickData")
            ],
        ),
        vm.Card(id="my_card_1", text="Click on a point on the above graph."),
        vm.Card(id="my_card_2", text="Click on a point on the above graph."),
    ],
    controls=[vm.Filter(column="species", selector=vm.Dropdown(title="Species"))],
)


########### MS EXAMPLE ###########
### PAGE 3 ###########
# This is the callback replacement for the action below
@callback(
    Output("slider_continent", "value", allow_duplicate=True),
    Output("card_cross_filter", "children", allow_duplicate=True),
    Input("underlying_grid", "cellClicked"),
    prevent_initial_call=True,
)
def parameter_interaction_callback(cell_data: dict):
    if cell_data is None:
        return 0, "No cell clicked"
    index = cell_data["rowIndex"]
    return index, f"cell_data: {cell_data}"


# This action doesn't fully work, because the slider update does not trigger the new data loading
@capture("action")
def parameter_interaction(cell_data: dict):
    return str(cell_data["rowIndex"]), cell_data["rowIndex"]


# Fake slow loading
def slow_load_gapminder():
    time.sleep(2)
    return px.data.gapminder()


# This is essentially a filter replacement, but done via parameters, so it can take advantage of caching
# Fake it also to be very slow
def filter_gapminder_continent_via_index(index: int):
    print("Loading gapminder filtered")
    gapminder = data_manager["gapminder"].load()
    time.sleep(2)  # Fake slow loading / and/or calculation
    continent = gapminder["continent"][index]
    return gapminder[gapminder["continent"] == continent]


data_manager.cache = Cache(config={"CACHE_TYPE": "SimpleCache"})


df_gapminder = px.data.gapminder()
data_manager["gapminder"] = slow_load_gapminder
data_manager["gapminder_filtered"] = filter_gapminder_continent_via_index

vm.Page.add_type("components", vm.Dropdown)

page_3 = vm.Page(
    title="[MS Experiment] Advanced filter interaction and caching calculations",
    components=[
        vm.AgGrid(
            id="grid",
            figure=dash_ag_grid(id="underlying_grid", data_frame=df_gapminder),
            footer="Clicking here will trigger a slow calculation/filtering operation, but if you click the same row multiple times, it will use the cached result.",
            # TODO: This doesn't work, but it somewhat should in the future!
            # actions=[
            #     vm.Action(
            #         function=parameter_interaction("underlying_grid.cellClicked"),
            #         outputs=["card_cross_filter.children", "slider_continent.value"],
            #     )
            # ],
        ),
        vm.Graph(
            id="slow_load_chart",
            figure=px.scatter("gapminder_filtered", x="gdpPercap", y="lifeExp", color="continent"),
            footer="This is the result of the slow calculation/filtering operation - filtered by the continent of the selected row.",
        ),
        vm.Card(id="card_cross_filter", text="Click on a point on the above table."),
        vm.Text(
            text="""This example showcases how to cache a calculation that may be slow. 
                It was attempted with actions, but it didn't work.
                Reason is that the updated slider does not trigger the new data loading.
                
                Beyond that, it also shows how one can do advanced filter interactions without using a filter (not always good),
                but importantly without returning an entire chart component.
                """
        ),
    ],
    controls=[
        vm.Parameter(
            targets=["slow_load_chart.data_frame.index"],
            selector=vm.Slider(id="slider_continent", min=0, max=df_gapminder.shape[0] - 1, step=1),
        )
    ],
    layout=vm.Layout(
        grid=[[0, 1], [0, 1], [2, 2], [3, 3]],
    ),
)
# In future:
# - do action directly and not a callback
# - initial plan: somehow enable to send data from arbitrary column of row, or cell
# - if more than one value, that is not possible, need to have two filters
# - parametrized data ops: hooks, which you can inject, gives clearer overview: new Filter, Parameter


########### PAGE 4 ###########
vm.Page.add_type("controls", vm.Dropdown)
vm.Page.add_type("controls", vm.RangeSlider)
vm.Page.add_type("controls", vm.RadioItems)


# Update the store with both values
@callback(
    Output("store_1", "data"),
    Input("dropdown_alone", "value"),
    Input("slider_alone", "value"),
)
def update_store_1(dropdown_value, slider_value):
    return {"dropdown_value": dropdown_value, "slider_value": slider_value}


# Update the card with the store data
@callback(
    Output("card_delayed", "children"),
    Input("button_delayed", "n_clicks"),
    State("store_1", "data"),
)
def update_card_delayed(n_clicks, store_1_data):
    return f"Store 1 data: {store_1_data}"


page_4 = vm.Page(
    title="[MS Experiment] Grouped/delayed execution (with callbacks)",
    components=[
        vm.Button(id="button_delayed", text="Make it happen"),
        vm.Card(id="card_delayed", text="Nothing configured yet"),
        vm.Text(
            text="""This example shows delayed and grouped execution, ultimately what some form of Form (no pun intended) should be able to do.
                How to affect either chart, or data loading? ==> use a parameter, but then we have to have a target. See next example for a take on that.

                This seemed impossible to do with actions as is, so entirely reverted to callbacks.
                """
        ),
    ],
    controls=[
        vm.Dropdown(
            id="dropdown_alone",
            options=df_gapminder["continent"].unique(),
            value="Asia",
        ),
        vm.RangeSlider(id="slider_alone", min=0, max=120000, step=20000, value=[0, 80000]),
        # Cannot use proper controls here, as I cannot target a captured callable? Parameter would allow the caching....
    ],
)

# Future:
# - some form of lazy control, if lazy: need a submit
# - control group?: group with a button, but keep filter and parameter
# - add arbitrary key value pairs is feasible, component on it's own
# - Standalon form?: in either case: what gets send and what gets received need to check (unpacking etc)
# Catch: do we use pattern matching callbacks?

########### PAGE 5 ###########


# First very! early attempt at a state component, which I really think we should have in a cool form in Vizro
class VizroState(vm.VizroBaseModel):
    """New custom component `State`."""

    type: Literal["state"] = "state"
    data: Optional[dict[str, Any]]  # would be interesting to connect this to pydantic models
    # Note sure if the actions work at all... I think the trigger is the problem
    actions: Annotated[
        list[ActionType],
        AfterValidator(_action_validator_factory("data")),
        PlainSerializer(lambda x: x[0].actions),
        Field(default=[]),
    ]

    @_log_call
    def build(self):
        return dcc.Store(id=self.id, data=self.data or {}, storage_type="session")


vm.Page.add_type("components", VizroState)


# class StateA(BaseModel):
#     dropdown_value: list[str]


@capture("action")
def update_state_with_action(dropdown_value):
    print("update_store_with_action", dropdown_value)
    return {"dropdown_value": [dropdown_value]}


# Replacement for action that doesn't work
@callback(
    [
        Output("user_input_via_store_model", "value"),
        Output("card_via_store_model", "children"),
    ],
    State("store_model", "data"),
    Input("button_delayed_via_state", "n_clicks"),
)
def update_user_input_and_card_from_state(state_data, n_clicks):
    if n_clicks is None:
        return "", ""
    return state_data["dropdown_value"], f"State data: {state_data}"


# This does not work
@capture("action")
def update_card_and_input_from_state(state_data):
    print("update_card_from_state", state_data)
    return f"State data: {state_data}", str(state_data["dropdown_value"])


# This works, and updates the card from the store
# @callback(Output("card_via_store_model", "children"), Input("store_model", "data"))
# def update_card_from_state(state_data):
#     print("update_card_from_state", state_data)
#     return f"State data: {state_data}"


# This is essentially a filter replacement, but done via parameters, so it can take advantage of caching
def filter_gapminder_continent_via_text_area(continent: str):
    print("Loading gapminder filtered for continent", continent)
    gapminder = data_manager["gapminder"].load()
    time.sleep(2)  # Fake slow loading / and/or calculation
    if not continent:
        return gapminder
    # Check if continent is a list of lists (like [['Asia', 'Europe']])
    if isinstance(continent, list) and continent and isinstance(continent[0], list):
        # Extract the inner list of continents
        continents = continent[0]
        return gapminder[gapminder["continent"].isin(continents)]
    else:
        # Handle the original single continent case
        return gapminder[gapminder["continent"] == continent]


data_manager["gapminder_filtered_via_text_area"] = filter_gapminder_continent_via_text_area

vm.Parameter.add_type("selector", TextArea)
vm.Parameter.add_type("selector", UserInput)


page_5 = vm.Page(
    title="[MS Experiment] Grouped/delayed execution (with State)",
    components=[
        vm.Graph(
            id="delayed_chart_via_state",
            figure=px.scatter(
                "gapminder_filtered_via_text_area",
                x="gdpPercap",
                y="lifeExp",
                color="continent",
            ),
            footer="This is the result of the slow calculation/filtering operation - filtered by the continent of the selected row.",
        ),
        vm.Button(
            id="button_delayed_via_state",
            text="Make it happen",
            # actions=[
            #     vm.Action(
            #         function=update_card_and_input_from_state("store_model.data"),
            #         outputs=["card_via_store_model.children", "user_input_via_store_model.value"],
            #     )
            # ],
        ),
        VizroState(
            id="store_model",
            data={"dropdown_value": ["Asia"]},
            # This does not work, but the callback does!
            # actions=[
            #     vm.Action(
            #         function=update_card_from_state("store_model.data"), outputs=["card_via_store_model.children"]
            #     )
            # ],
        ),
        vm.Card(id="card_via_store_model", text="Nothing configured yet"),
    ],
    controls=[
        vm.Dropdown(
            id="dropdown_via_store_model",
            options=df_gapminder["continent"].unique(),
            value="Asia",
            actions=[
                vm.Action(
                    function=update_state_with_action("dropdown_via_store_model.value"),
                    outputs=["store_model.data"],
                )
            ],
        ),
        vm.Parameter(
            id="parameter_via_state",
            targets=["delayed_chart_via_state.data_frame.continent"],  # delayed_chart_via_state.data_frame.continent
            selector=UserInput(id="user_input_via_store_model"),  # For some reason TextArea doesn't work
        ),
    ],
)

########### MS EXAMPLE ###########

dashboard = vm.Dashboard(pages=[page_1, page_2, page_3, page_4, page_5])

if __name__ == "__main__":
    app = Vizro().build(dashboard)
    app.dash.layout.children.append(dcc.Store(id="store_1", storage_type="session"))
    app.run()


# TODO:
# for actual PR review, test having access to controls, but again Parameters need to have a target
# Weave in pydantic for better state management
# how to better update the state selectively?
# how to better draw from the state into other things?
# try state with drill through?
