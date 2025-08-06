# # Vizro is an open-source toolkit for creating modular data visualization applications.
# # check out https://github.com/mckinsey/vizro for more info about Vizro
# # and checkout https://vizro.readthedocs.io/en/stable/ for documentation.

import json
import random
import time
from time import sleep
from typing import Any, Literal, Optional

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import vizro.models as vm
import vizro.plotly.express as px
from dash import ALL, Input, Output, State, callback, callback_context, dash, dcc, html, no_update

# from ploomber_cloud import functions
from vizro import Vizro
from vizro.actions import export_data, filter_interaction
from vizro.managers import data_manager
from vizro.models._models_utils import _log_call
from vizro.models.types import capture
from vizro.tables import dash_ag_grid, dash_data_table


class VizroStore(vm.VizroBaseModel):
    id: str
    type: Literal["vizro_store"] = "vizro_store"

    @_log_call
    def build(self):
        return dcc.Store(id=self.id, storage_type="session")


vm.Container.add_type("components", VizroStore)
vm.Page.add_type("components", VizroStore)
vm.Page.add_type("controls", vm.Slider)
vm.Page.add_type("controls", vm.RadioItems)
vm.Page.add_type("controls", vm.Button)

df_gapminder = px.data.gapminder().query("year == 2007")


def load_dynamic_gapminder_data(continent: str = "Europe"):
    return df_gapminder[df_gapminder["continent"] == continent]


data_manager["dynamic_df_gapminder_arg"] = load_dynamic_gapminder_data
data_manager["dynamic_df_gapminder"] = lambda: df_gapminder


page_1 = vm.Page(
    title="My first dashboard",
    components=[
        # vm.Graph(figure=px.scatter("dynamic_df_gapminder", x="gdpPercap", y="lifeExp", size="pop", color="continent")),
        vm.Graph(figure=px.histogram(df_gapminder, x="lifeExp", color="continent", barmode="group")),
    ],
    controls=[
        vm.Filter(column="continent", id="f", show_in_url=True),
    ],
)


# PAGE 2 = Test store concept and slow calculations
@capture("action")
def reset_store():
    return {}


@capture("action")
def update_card_text(input_param: str, store: Optional[dict[str, Any]]):
    store = store or {}
    return f"You selected species **{input_param}** and the store is {store}"


@capture("action")
def update_store_from_selectors(input_param: str, store: Optional[dict[str, Any]]):
    store = store or {}
    store["current_params"] = input_param
    return store


# PR[MS]: I could not get this to work, but didn't try too hard. Looked like i was struggling on Ploomber side
# In general I think this sort of thing is a good example how how people should handle potentially model interactions
# Generally speaking I am also interested in dash[async] for DB access etc - also see the non-blocking comment below
# @functions.serverless(requirements=["scikit-learn==1.4.0"])
def square(x: int, delay: int = 0):
    time.sleep(delay)
    return x**2


@capture("action")
def mega_calculation(store: Optional[dict[str, Any]], delay: int = 0):
    store = store or {}
    calculation_id = f"calculation_{time.time()}"
    result = square(store["current_params"], delay)
    store[calculation_id] = {
        "params": store["current_params"],
        "result": f"The square of {store['current_params']} is {result}",
    }
    return store


page_2 = vm.Page(
    title="Using a store and simulating model run",
    components=[
        VizroStore(id="page2-store"),
        vm.Graph(figure=px.scatter(df_gapminder, x="gdpPercap", y="lifeExp", size="pop", color="continent")),
        vm.Card(text="Placeholder text", id="my_card"),
    ],
    layout=vm.Grid(grid=[["1", "2"], ["0", "0"]]),
    controls=[
        vm.RadioItems(id="radio", options=[0, 1, 5], value=0, title="How mega the calculation is"),
        vm.Slider(
            id="slider",
            title="Square this number",
            min=0,
            max=5,
            step=0.5,
            value=2,
            actions=[
                vm.Action(
                    function=update_store_from_selectors(),
                    inputs=["slider.value", "page2-store.data"],
                    outputs=["page2-store.data"],
                ),
                # PR[MS]: this only triggers on selector change - resets to default on Page refresh
                vm.Action(
                    function=update_card_text(),
                    inputs=["slider.value", "page2-store.data"],
                    outputs=["my_card.text"],
                ),
            ],
        ),
        # PR[MS]: Seems to be non-blocking (good) so that I can switch page, however
        # fails if the output is not anymore on the page  (bad) -> not sure what we desire
        vm.Button(
            text="Click me!",
            actions=[
                vm.Action(
                    function=update_store_from_selectors(),
                    inputs=["slider.value", "page2-store.data"],
                    outputs=["page2-store.data"],
                ),
                vm.Action(
                    function=mega_calculation(),
                    inputs=["page2-store.data", "radio.value"],
                    outputs=["page2-store.data"],
                ),
                vm.Action(
                    function=update_card_text(),
                    inputs=["slider.value", "page2-store.data"],
                    outputs=["my_card.text"],
                ),
            ],
        ),
        vm.Button(
            text="Reset store",
            actions=[
                vm.Action(
                    function=reset_store(),
                    outputs=["page2-store.data"],
                ),
            ],
        ),
    ],
)


# PAGE 3 - Double filtering due to Pivoted data
# PR[MS]: This works overall pretty great now - ideally it can be simplified with a predefined action
# and maybe with less filter creation??
@capture("graph")
def heatmap(data_frame: pd.DataFrame) -> go.Figure:
    fig = px.imshow(
        data_frame,
        text_auto=True,  # Show the values on the heatmap
        labels=dict(x="Company", y="Product", color="Average Sales"),
        # color_continuous_scale="Viridis",
    )

    fig.update_layout(
        title="Average Sales by Product and Company",
        xaxis_title="Company",
        yaxis_title="Product",
    )

    return fig


def generate_random_dataset(num_samples_per_combination: int = 5) -> pd.DataFrame:
    companies = ["Apple", "Microsoft", "Amazon", "Google"]
    products = ["Smartphones", "Laptops", "Tablets", "Wearables"]
    channels = ["Online", "Retail", "Direct Sales"]
    data = {"Product": [], "Company": [], "Channel": [], "Sales": []}
    for product in products:
        for company in companies:
            for _ in range(num_samples_per_combination):
                data["Product"].append(product)
                data["Company"].append(company)
                channel = random.choice(channels)
                data["Channel"].append(channel)
                sales = random.randint(100, 10000)
                data["Sales"].append(sales)

    return pd.DataFrame(data)


df_sales = generate_random_dataset(num_samples_per_combination=3)
# Create a pivot table to calculate average sales for each Product-Company combination
df_sales_pivot = df_sales.pivot_table(
    index="Product",
    columns="Company",
    values="Sales",
    aggfunc="mean",  # Calculate the average sales
)


@capture("action")
def update_card_text_2(click_data: dict):
    """Update card text with click data information."""
    if not click_data:
        return "No data selected. Click on the heatmap to see details."

    return f"Click data: {click_data}"


@capture("action")
def update_filter_selectors(click_data: dict[str, Any]) -> tuple[Optional[str], Optional[str]]:
    """Update filter selectors based on heatmap click data."""
    if not click_data or "points" not in click_data:
        return None, None
    point = click_data["points"][0]
    company = point.get("x")
    product = point.get("y")
    return company, product


page_3 = vm.Page(
    title="Filter interaction graph",
    layout=vm.Grid(grid=[["0", "1"], ["0", "1"], ["0", "2"]]),
    components=[
        vm.Graph(
            id="heatmap",
            figure=heatmap(df_sales_pivot),
            actions=[
                vm.Action(
                    function=update_card_text_2(),
                    inputs=["heatmap.clickData"],
                    outputs=["my_card_2.text"],
                ),
                vm.Action(
                    function=update_filter_selectors(),
                    inputs=["heatmap.clickData"],
                    outputs=["filter_company_selector.value", "filter_product_selector.value"],
                ),
            ],
        ),
        vm.AgGrid(
            id="ag_grid_interaction",
            figure=dash_ag_grid(data_frame=df_sales),
        ),
        vm.Card(text="Placeholder text", id="my_card_2"),
    ],
    controls=[
        vm.Filter(
            targets=["ag_grid_interaction"],
            column="Company",
            selector=vm.Dropdown(id="filter_company_selector"),
            id="filter_company",
        ),
        vm.Filter(
            targets=["ag_grid_interaction"],
            column="Product",
            selector=vm.Dropdown(id="filter_product_selector"),
            id="filter_product",
        ),
    ],
)


# PAGE 4 - Action creating new components, that maybe themselves can target/be targeted by other actions
"""
I think we should try and simulate a ToDo list as an example of a CRUD application

Feedback:
- It is possible until we want to target individual items of the list --> then we start needing (I think) pattern matching stuff
- Overall the two main dash functionalities are: Pattern matching and some form of custom figure
- the figure is really just a dummy to target with an action
- For my liking this is still too much dash, but the million dollar question is: how to make this Vizro only?? Do we even
want this?
- Would All in one components that we publish be a good idea? Or maybe custom react components that we can target with just actions?

"""


@capture("figure")
def placeholder_card(data_frame: pd.DataFrame) -> html.Div:
    return html.Div([dbc.Card(dcc.Markdown("Placeholder text"))])


@capture("action")
def add_todo_to_store(text: str, store: Optional[dict[str, Any]]):
    store = store or {}
    store.setdefault("todos", [])
    todos = store["todos"]

    highest_id = max([todo.get("id", 0) for todo in todos], default=0) if todos else 0
    todos.append({"id": highest_id + 1, "text": text, "completed": False})

    return store


@capture("action")
def update_todos_figure(store: Optional[dict[str, Any]]):
    store = store or {}
    todos = store.get("todos", [])
    return html.Div(
        [
            html.Div(
                [
                    dcc.Checklist(
                        options=[{"label": "", "value": f"todo_{todo['id']}"}],
                        value=[f"todo_{todo['id']}"] if todo["completed"] else [],
                        inline=True,
                        style={"display": "inline-block", "marginRight": "10px"},
                        id={"type": "todo-checklist", "index": todo["id"]},  # Dictionary ID for pattern matching
                    ),
                    dbc.Card(
                        dcc.Markdown(f"### Todo #{todo['id']}\n{todo['text']}"),
                        style={"display": "inline-block", "width": "90%"},
                    ),
                ],
                style={"display": "flex", "alignItems": "center", "marginBottom": "10px"},
            )
            for todo in todos
        ],
        className="multiple-cards-container",
    )


@callback(
    Output("store_page_4", "data"),
    Input({"type": "todo-checklist", "index": ALL}, "value"),
    State("store_page_4", "data"),
    prevent_initial_call=True,
)
def checklist_pattern_callback(checklist_values: list, store: Optional[dict[str, Any]]):
    """Pattern matching callback that responds to any checklist change"""

    if not callback_context.triggered:
        return no_update

    # Pattern matching callback -> this bit is basically not possible for Vizro I suppose?
    triggered_id = callback_context.triggered[0]["prop_id"]
    component_id = json.loads(triggered_id.split(".")[0])
    todo_index = component_id["index"]

    triggered_value = callback_context.triggered[0]["value"]
    is_checked = len(triggered_value) > 0  # If list is not empty, it's checked

    store = store or {}
    todos = store.get("todos", [])
    for todo in todos:
        if todo["id"] == todo_index:
            todo["completed"] = is_checked
            break

    store["todos"] = todos
    return store


@capture("action")
def reset_store_page_4():
    store = {}
    store["todos"] = []
    return store


@capture("action")
def remove_done_todos(store: Optional[dict[str, Any]]):
    store = store or {}
    todos = store.get("todos", [])
    store["todos"] = [todo for todo in todos if not todo["completed"]]
    return store


vm.Page.add_type("components", vm.TextArea)

page_4 = vm.Page(
    title="Action creating new components (CRUD) application",
    layout=vm.Grid(grid=[[0, 1, 2, 4, 5], [3, 3, 3, 3, 3], [3, 3, 3, 3, 3], [3, 3, 3, 3, 3]]),
    components=[
        vm.TextArea(id="text_area"),
        vm.Button(
            text="Add",
            id="button_add",
            actions=[
                vm.Action(
                    function=add_todo_to_store(),
                    inputs=["text_area.value", "store_page_4.data"],
                    outputs=["store_page_4.data"],
                ),
                vm.Action(
                    function=update_todos_figure(),
                    inputs=["store_page_4.data"],
                    outputs=["figure_1.children"],
                ),
            ],
        ),
        vm.Button(
            text="Remove done",
            id="button_remove_done",
            actions=[
                vm.Action(function=remove_done_todos(), inputs=["store_page_4.data"], outputs=["store_page_4.data"]),
                vm.Action(function=update_todos_figure(), inputs=["store_page_4.data"], outputs=["figure_1.children"]),
            ],
        ),
        # PR[MS]: Again this resets on page refresh - we probably need an action that attaches to `on_page_load`
        vm.Figure(id="figure_1", figure=placeholder_card(df_gapminder)),
        vm.Button(
            text="Reset ToDo list",
            id="button_reset",
            actions=[
                vm.Action(function=reset_store_page_4(), outputs=["store_page_4.data"]),
                vm.Action(function=update_todos_figure(), inputs=["store_page_4.data"], outputs=["figure_1.children"]),
            ],
        ),
        VizroStore(id="store_page_4"),
    ],
)

dashboard = vm.Dashboard(pages=[page_1, page_2, page_3, page_4])

app = Vizro().build(dashboard)

if __name__ == "__main__":
    # PR[MS]: Debug mode does not reload anymore?!
    app.run(debug=True)
