"""Example page for the Cascader component in leaf mode (`full_path=False`, the default).

Every selection's `value` is the bare leaf scalar (single-select) or a list of leaf scalars
(multi-select), matching the pre-0.2 behaviour. Leaf values must be unique across the whole tree;
for trees with duplicate leaf labels across branches use path mode (`full_path=True`, see the
"Cascader (path)" page).
"""

# ruff: noqa: D103

import dash
import dash_mantine_components as dmc
import vizro_dash_components as vdc
from dash import Input, Output, callback, ctx, html

dash.register_page(__name__, name="Cascader (leaf)", title="Cascader (leaf)")

MAX_WIDTH = 400

# --- Option trees (leaf values are unique across the whole tree, as leaf mode requires) ---

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
        "Brazil": ["Sao Paulo", "Rio de Janeiro", "Brasilia", "Salvador"],
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
        "Men's": ["Shirts", "Trousers", "Men's Shoes"],
        "Women's": ["Dresses", "Tops", "Women's Shoes"],
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
            "Click through the tree to select a leaf. The emitted value is the bare leaf scalar.",
            html.Div(
                [
                    vdc.Cascader(id="leaf-single", options=LOCATIONS, placeholder="Select a city..."),
                    value_out("leaf-single-out"),
                ],
                style={"maxWidth": MAX_WIDTH},
            ),
        ),
        section(
            "Single-select with pre-set value",
            'The value is a bare leaf, e.g. "Tokyo".',
            html.Div(
                [
                    vdc.Cascader(id="leaf-single-preseeded", options=LOCATIONS, value="Tokyo"),
                    value_out("leaf-single-preseeded-out"),
                ],
                style={"maxWidth": MAX_WIDTH},
            ),
        ),
        section(
            "Multi-select",
            "Checkboxes with tri-state (checked / indeterminate / unchecked). Value is a list of leaf scalars.",
            html.Div(
                [
                    vdc.Cascader(id="leaf-multi", options=LOCATIONS, multi=True, placeholder="Select cities..."),
                    value_out("leaf-multi-out"),
                ],
                style={"maxWidth": MAX_WIDTH},
            ),
        ),
        section(
            "Multi-select with pre-set values",
            'The value is a list of bare leaves, e.g. ["Tokyo", "Paris", "Berlin"].',
            html.Div(
                [
                    vdc.Cascader(
                        id="leaf-multi-preseeded",
                        options=LOCATIONS,
                        multi=True,
                        value=["Tokyo", "Paris", "Berlin"],
                    ),
                    value_out("leaf-multi-preseeded-out"),
                ],
                style={"maxWidth": MAX_WIDTH},
            ),
        ),
        section(
            "Different option tree",
            "Any nested dict/list structure works, as long as leaf values are unique.",
            html.Div(
                [
                    vdc.Cascader(id="leaf-products", options=PRODUCTS, multi=True, placeholder="Select products..."),
                    value_out("leaf-products-out"),
                ],
                style={"maxWidth": MAX_WIDTH},
            ),
        ),
        section(
            "Leaf values must be unique",
            "In leaf mode a selection is identified by its leaf alone, so duplicate leaf labels across "
            "branches are ambiguous and log a console error. Switch to path mode to support them "
            '(see the "Cascader (path)" page).',
            None,
        ),
        section(
            "Not searchable, not clearable",
            "searchable=False hides the search input. clearable=False hides the X button.",
            html.Div(
                vdc.Cascader(
                    id="leaf-no-search",
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
                        vdc.Cascader(
                            id="leaf-disabled-empty", options=LOCATIONS, disabled=True, placeholder="Disabled..."
                        ),
                        style={"width": MAX_WIDTH},
                    ),
                    html.Div(
                        vdc.Cascader(id="leaf-disabled-val", options=LOCATIONS, disabled=True, value="Tokyo"),
                        style={"width": MAX_WIDTH},
                    ),
                ],
                align="start",
            ),
        ),
        section(
            "Programmatic value update",
            "Buttons set the Cascader value (a bare leaf) via a callback.",
            html.Div(
                [
                    dmc.Group(
                        [
                            dmc.Button("Set Tokyo", id="leaf-btn-tokyo", variant="outline", size="sm"),
                            dmc.Button("Set Paris", id="leaf-btn-paris", variant="outline", size="sm"),
                            dmc.Button("Clear", id="leaf-btn-clear", variant="outline", size="sm", color="red"),
                        ],
                        mb="sm",
                    ),
                    vdc.Cascader(id="leaf-programmatic", options=LOCATIONS, placeholder="Driven by buttons..."),
                    value_out("leaf-programmatic-out"),
                ],
                style={"maxWidth": MAX_WIDTH},
            ),
        ),
        section(
            "Constrained height (maxHeight=150)",
            "Each column scrolls independently within the constrained panel height.",
            html.Div(
                vdc.Cascader(id="leaf-maxheight", options=LOCATIONS, multi=True, maxHeight=150),
                style={"maxWidth": MAX_WIDTH},
            ),
        ),
        html.Div(style={"height": "200px"}),
    ]
)


@callback(Output("leaf-single-out", "children"), Input("leaf-single", "value"))
def show_single(v):
    return f"value: {v!r}"


@callback(Output("leaf-single-preseeded-out", "children"), Input("leaf-single-preseeded", "value"))
def show_single_preseeded(v):
    return f"value: {v!r}"


@callback(Output("leaf-multi-out", "children"), Input("leaf-multi", "value"))
def show_multi(v):
    return f"value: {sorted(v or [])!r}"


@callback(Output("leaf-multi-preseeded-out", "children"), Input("leaf-multi-preseeded", "value"))
def show_multi_preseeded(v):
    return f"value: {sorted(v or [])!r}"


@callback(Output("leaf-products-out", "children"), Input("leaf-products", "value"))
def show_products(v):
    return f"value: {sorted(v or [])!r}"


@callback(
    Output("leaf-programmatic", "value"),
    Input("leaf-btn-tokyo", "n_clicks"),
    Input("leaf-btn-paris", "n_clicks"),
    Input("leaf-btn-clear", "n_clicks"),
    prevent_initial_call=True,
)
def set_programmatic(_t, _p, _c):
    if ctx.triggered_id == "leaf-btn-tokyo":
        return "Tokyo"
    if ctx.triggered_id == "leaf-btn-paris":
        return "Paris"
    return None


@callback(Output("leaf-programmatic-out", "children"), Input("leaf-programmatic", "value"))
def show_programmatic(v):
    return f"value: {v!r}"
