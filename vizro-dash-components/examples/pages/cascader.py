"""Feature showcase for the Cascader component."""

# ruff: noqa: D103

import dash
import dash_mantine_components as dmc
from dash import Input, Output, callback, ctx, html
from vizro_dash_components import Cascader

dash.register_page(__name__, path="/cascader", name="Cascader", order=0)

MAX_WIDTH = 400

# --- Option trees ---

LOCATIONS = {
    "Asia": {
        "Japan": ["Tokyo", "Osaka", "Kyoto", "Yokohama"],
        "China": ["Beijing", "Shanghai", "Shenzhen", "Guangzhou"],
        "India": ["Mumbai", "Delhi", "Bangalore", "Chennai"],
    },
    "Europe": {
        "France": ["Paris", "Lyon", "Marseille", "Toulouse"],
        "Germany": ["Berlin", "Munich", "Hamburg", "Frankfurt"],
        "UK": ["London", "Manchester", "Birmingham", "Edinburgh"],
    },
    "Americas": {
        "USA": ["New York", "Los Angeles", "Chicago", "Houston"],
        "Brazil": ["São Paulo", "Rio de Janeiro", "Brasília", "Salvador"],
        "Canada": ["Toronto", "Vancouver", "Montreal", "Calgary"],
    },
}

PRODUCTS = {
    "Electronics": {
        "Computers": ["Laptops", "Desktops", "Tablets"],
        "Phones": ["Smartphones", "Feature Phones"],
        "Audio": ["Headphones", "Speakers", "Earbuds"],
    },
    "Clothing": {
        "Men's": ["Shirts", "Trousers", "Shoes"],
        "Women's": ["Dresses", "Tops", "Shoes"],
    },
    "Food & Drink": {
        "Beverages": ["Coffee", "Tea", "Juice"],
        "Snacks": ["Chips", "Chocolate", "Nuts"],
    },
}


def section(title, description, *content):
    return html.Div(
        [
            dmc.Title(title, order=2, mb=4),
            dmc.Text(description, c="dimmed", size="sm", mb="sm") if description else None,
            *content,
            dmc.Divider(mt="xl", mb="xl"),
        ]
    )


def value_out(id):
    return dmc.Text(id=id, size="xs", c="dimmed", mt=4)


layout = html.Div(
    [
        section(
            "Single-select",
            "Click through the tree to select a leaf value. The panel closes on selection.",
            html.Div(
                [Cascader(id="single", options=LOCATIONS, placeholder="Select a city..."), value_out("single-out")],
                style={"maxWidth": MAX_WIDTH},
            ),
        ),
        section(
            "Single-select with pre-set value",
            None,
            html.Div(
                [Cascader(id="single-preseeded", options=LOCATIONS, value="Tokyo"), value_out("single-preseeded-out")],
                style={"maxWidth": MAX_WIDTH},
            ),
        ),
        section(
            "Multi-select",
            "Checkboxes with tri-state (checked / indeterminate / unchecked). "
            "Count badge shown when more than one item is selected.",
            html.Div(
                [
                    Cascader(id="multi", options=LOCATIONS, multi=True, placeholder="Select cities..."),
                    value_out("multi-out"),
                ],
                style={"maxWidth": MAX_WIDTH},
            ),
        ),
        section(
            "Multi-select with pre-set values",
            None,
            html.Div(
                [
                    Cascader(id="multi-preseeded", options=LOCATIONS, multi=True, value=["Tokyo", "Paris", "Berlin"]),
                    value_out("multi-preseeded-out"),
                ],
                style={"maxWidth": MAX_WIDTH},
            ),
        ),
        section(
            "Different option tree",
            "Any nested dict/list structure works.",
            html.Div(
                [
                    Cascader(id="products", options=PRODUCTS, multi=True, placeholder="Select products..."),
                    value_out("products-out"),
                ],
                style={"maxWidth": MAX_WIDTH},
            ),
        ),
        section(
            "Not searchable, not clearable",
            "searchable=False hides the search input. clearable=False hides the X button.",
            html.Div(
                Cascader(
                    id="no-search",
                    options=LOCATIONS,
                    searchable=False,
                    clearable=False,
                    placeholder="Pick a city...",
                ),
                style={"maxWidth": MAX_WIDTH},
            ),
        ),
        section(
            "Disabled",
            None,
            dmc.Group(
                [
                    html.Div(
                        Cascader(id="disabled-empty", options=LOCATIONS, disabled=True, placeholder="Disabled..."),
                        style={"width": MAX_WIDTH},
                    ),
                    html.Div(
                        Cascader(id="disabled-val", options=LOCATIONS, disabled=True, value="Tokyo"),
                        style={"width": MAX_WIDTH},
                    ),
                ],
                align="start",
            ),
        ),
        section(
            "Programmatic value update",
            "Buttons set the Cascader value via a callback.",
            html.Div(
                [
                    dmc.Group(
                        [
                            dmc.Button("Set Tokyo", id="btn-tokyo", variant="outline", size="sm"),
                            dmc.Button("Set Paris", id="btn-paris", variant="outline", size="sm"),
                            dmc.Button("Clear", id="btn-clear", variant="outline", size="sm", color="red"),
                        ],
                        mb="sm",
                    ),
                    Cascader(id="programmatic", options=LOCATIONS, placeholder="Driven by buttons..."),
                    value_out("programmatic-out"),
                ],
                style={"maxWidth": MAX_WIDTH},
            ),
        ),
        section(
            "Constrained height (maxHeight=150)",
            "Each column scrolls independently within the constrained panel height.",
            html.Div(
                Cascader(id="maxheight", options=LOCATIONS, multi=True, maxHeight=150),
                style={"maxWidth": MAX_WIDTH},
            ),
        ),
        html.Div(style={"height": "200px"}),
    ]
)


@callback(Output("single-out", "children"), Input("single", "value"))
def show_single(v):
    return f"value: {v}"


@callback(Output("single-preseeded-out", "children"), Input("single-preseeded", "value"))
def show_single_preseeded(v):
    return f"value: {v}"


@callback(Output("multi-out", "children"), Input("multi", "value"))
def show_multi(v):
    return f"value: {sorted(v or [])}"


@callback(Output("multi-preseeded-out", "children"), Input("multi-preseeded", "value"))
def show_multi_preseeded(v):
    return f"value: {sorted(v or [])}"


@callback(Output("products-out", "children"), Input("products", "value"))
def show_products(v):
    return f"value: {sorted(v or [])}"


@callback(
    Output("programmatic", "value"),
    Input("btn-tokyo", "n_clicks"),
    Input("btn-paris", "n_clicks"),
    Input("btn-clear", "n_clicks"),
    prevent_initial_call=True,
)
def set_programmatic(_t, _p, _c):
    if ctx.triggered_id == "btn-tokyo":
        return "Tokyo"
    if ctx.triggered_id == "btn-paris":
        return "Paris"
    return None


@callback(Output("programmatic-out", "children"), Input("programmatic", "value"))
def show_programmatic(v):
    return f"value: {v}"
