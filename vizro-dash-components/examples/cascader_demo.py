"""Full-suite demo for the Cascader component."""

import dash_mantine_components as dmc
from dash import Dash, Input, Output, ctx, dcc, html
from vizro_dash_components import Cascader

# --- Option trees ---

WORLD_OPTIONS = [
    {
        "label": "Asia",
        "value": "asia",
        "children": [
            {
                "label": "East Asia",
                "value": "east_asia",
                "children": [
                    {"label": "Japan", "value": "japan"},
                    {"label": "China", "value": "china"},
                    {"label": "South Korea", "value": "south_korea"},
                ],
            },
            {
                "label": "South Asia",
                "value": "south_asia",
                "children": [
                    {"label": "India", "value": "india"},
                    {"label": "Pakistan", "value": "pakistan"},
                    {"label": "Bangladesh", "value": "bangladesh"},
                ],
            },
            {
                "label": "Southeast Asia",
                "value": "sea",
                "children": [
                    {"label": "Thailand", "value": "thailand"},
                    {"label": "Vietnam", "value": "vietnam"},
                    {"label": "Indonesia", "value": "indonesia"},
                ],
            },
        ],
    },
    {
        "label": "Europe",
        "value": "europe",
        "children": [
            {
                "label": "Western Europe",
                "value": "western_europe",
                "children": [
                    {"label": "France", "value": "france"},
                    {"label": "Germany", "value": "germany"},
                    {"label": "Netherlands", "value": "netherlands"},
                ],
            },
            {
                "label": "Northern Europe",
                "value": "northern_europe",
                "children": [
                    {"label": "Sweden", "value": "sweden"},
                    {"label": "Norway", "value": "norway"},
                    {"label": "Denmark", "value": "denmark"},
                ],
            },
        ],
    },
    {
        "label": "Americas",
        "value": "americas",
        "children": [
            {
                "label": "North America",
                "value": "north_america",
                "children": [
                    {"label": "USA", "value": "usa"},
                    {"label": "Canada", "value": "canada"},
                    {"label": "Mexico", "value": "mexico"},
                ],
            },
            {
                "label": "South America",
                "value": "south_america",
                "children": [
                    {"label": "Brazil", "value": "brazil"},
                    {"label": "Argentina", "value": "argentina"},
                ],
            },
        ],
    },
]

PRODUCT_OPTIONS = [
    {
        "label": "Electronics",
        "value": "electronics",
        "children": [
            {
                "label": "Computers",
                "value": "computers",
                "children": [
                    {"label": "Laptops", "value": "laptops"},
                    {"label": "Desktops", "value": "desktops"},
                    {"label": "Tablets", "value": "tablets"},
                ],
            },
            {
                "label": "Phones",
                "value": "phones",
                "children": [
                    {"label": "Smartphones", "value": "smartphones"},
                    {"label": "Feature Phones", "value": "feature_phones"},
                ],
            },
            {
                "label": "Audio",
                "value": "audio",
                "children": [
                    {"label": "Headphones", "value": "headphones"},
                    {"label": "Speakers", "value": "speakers"},
                    {"label": "Earbuds", "value": "earbuds"},
                ],
            },
        ],
    },
    {
        "label": "Clothing",
        "value": "clothing",
        "children": [
            {
                "label": "Men's",
                "value": "mens",
                "children": [
                    {"label": "Shirts", "value": "mens_shirts"},
                    {"label": "Trousers", "value": "mens_trousers"},
                    {"label": "Shoes", "value": "mens_shoes"},
                ],
            },
            {
                "label": "Women's",
                "value": "womens",
                "children": [
                    {"label": "Dresses", "value": "womens_dresses"},
                    {"label": "Tops", "value": "womens_tops"},
                    {"label": "Shoes", "value": "womens_shoes"},
                ],
            },
        ],
    },
    {
        "label": "Food & Drink",
        "value": "food",
        "children": [
            {
                "label": "Beverages",
                "value": "beverages",
                "children": [
                    {"label": "Coffee", "value": "coffee"},
                    {"label": "Tea", "value": "tea"},
                    {"label": "Juice", "value": "juice", "disabled": True},
                ],
            },
            {
                "label": "Snacks",
                "value": "snacks",
                "children": [
                    {"label": "Chips", "value": "chips"},
                    {"label": "Chocolate", "value": "chocolate"},
                    {"label": "Nuts", "value": "nuts"},
                ],
            },
        ],
    },
]

STRESS_OPTIONS = [
    {
        "label": f"Category {i:02d}",
        "value": f"cat{i:02d}",
        "children": [
            {
                "label": f"Cat {i:02d} / Sub {j:02d}",
                "value": f"cat{i:02d}_sub{j:02d}",
                "children": [
                    {"label": f"Item {i:02d}-{j:02d}-{k:02d}", "value": f"item_{i:02d}_{j:02d}_{k:02d}"}
                    for k in range(10)
                ],
            }
            for j in range(10)
        ],
    }
    for i in range(10)
]


def _make_deep(prefix, depth):
    if depth == 0:
        return [{"label": f"Leaf {prefix}-{k}", "value": f"leaf_{prefix}_{k}"} for k in range(5)]
    return [
        {
            "label": f"Node {prefix}-{k}",
            "value": f"node_{prefix}_{k}",
            "children": _make_deep(f"{prefix}_{k}", depth - 1),
        }
        for k in range(5)
    ]


DEEP_OPTIONS = _make_deep("r", 4)

# --- Helpers ---


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


app = Dash(__name__, suppress_callback_exceptions=True)

app.layout = dmc.MantineProvider(
    dmc.Container(
        [
            dmc.Group(
                [
                    dmc.Title("Cascader — component showcase", order=1),
                    dmc.ColorSchemeToggle(
                        lightIcon=html.Span("☀", style={"fontSize": 20}),
                        darkIcon=html.Span("☾", style={"fontSize": 20}),
                        size="lg",
                    ),
                ],
                justify="space-between",
                align="center",
                mb="md",
            ),
            dmc.Divider(mb="xl"),
            section(
                "Single-select",
                "Leaf value set on click, panel closes, clear button resets to null.",
                dmc.Grid(
                    [
                        dmc.GridCol(
                            [
                                dmc.Text("Default", fw=600, size="sm", mb=4),
                                Cascader(id="single", options=WORLD_OPTIONS, placeholder="Select a country..."),
                                value_out("single-out"),
                            ],
                            span=6,
                        ),
                        dmc.GridCol(
                            [
                                dmc.Text("Pre-seeded: value='japan'", fw=600, size="sm", mb=4),
                                Cascader(id="single-preseeded", options=WORLD_OPTIONS, value="japan"),
                                value_out("single-preseeded-out"),
                            ],
                            span=6,
                        ),
                    ]
                ),
            ),
            section(
                "Multi-select",
                "Checkboxes stay open. Count badge when >1 selected. Select all / Deselect all.",
                dmc.Grid(
                    [
                        dmc.GridCol(
                            [
                                dmc.Text("Default", fw=600, size="sm", mb=4),
                                Cascader(id="multi", options=WORLD_OPTIONS, multi=True, placeholder="Select countries..."),
                                value_out("multi-out"),
                            ],
                            span=6,
                        ),
                        dmc.GridCol(
                            [
                                dmc.Text("Pre-seeded: japan + france + germany", fw=600, size="sm", mb=4),
                                Cascader(
                                    id="multi-preseeded",
                                    options=WORLD_OPTIONS,
                                    multi=True,
                                    value=["japan", "france", "germany"],
                                ),
                                value_out("multi-preseeded-out"),
                            ],
                            span=6,
                        ),
                    ]
                ),
            ),
            section(
                "searchable=False, clearable=False",
                None,
                dmc.Grid(
                    [
                        dmc.GridCol(
                            [
                                dmc.Text("Single-select", fw=600, size="sm", mb=4),
                                Cascader(
                                    id="no-search-single",
                                    options=WORLD_OPTIONS,
                                    searchable=False,
                                    clearable=False,
                                    placeholder="No search or clear...",
                                ),
                            ],
                            span=6,
                        ),
                        dmc.GridCol(
                            [
                                dmc.Text("Multi-select", fw=600, size="sm", mb=4),
                                Cascader(
                                    id="no-search-multi",
                                    options=WORLD_OPTIONS,
                                    multi=True,
                                    searchable=False,
                                    clearable=False,
                                    placeholder="No search or clear...",
                                ),
                            ],
                            span=6,
                        ),
                    ]
                ),
            ),
            section(
                "disabled=True",
                None,
                dmc.Grid(
                    [
                        dmc.GridCol(
                            [
                                dmc.Text("No value", fw=600, size="sm", mb=4),
                                Cascader(id="disabled-empty", options=WORLD_OPTIONS, disabled=True),
                            ],
                            span=3,
                        ),
                        dmc.GridCol(
                            [
                                dmc.Text("With value", fw=600, size="sm", mb=4),
                                Cascader(id="disabled-val", options=WORLD_OPTIONS, disabled=True, value="japan"),
                            ],
                            span=3,
                        ),
                        dmc.GridCol(
                            [
                                dmc.Text("Multi with value", fw=600, size="sm", mb=4),
                                Cascader(
                                    id="disabled-multi",
                                    options=WORLD_OPTIONS,
                                    multi=True,
                                    disabled=True,
                                    value=["japan", "france"],
                                ),
                            ],
                            span=6,
                        ),
                    ]
                ),
            ),
            section(
                "Programmatic value update",
                "Buttons drive the Cascader value from a callback.",
                dmc.Group(
                    [
                        dmc.Button("Set Japan", id="btn-japan", variant="outline", size="sm"),
                        dmc.Button("Set France", id="btn-france", variant="outline", size="sm"),
                        dmc.Button("Clear", id="btn-clear", variant="outline", size="sm", color="red"),
                    ],
                    mb="sm",
                ),
                Cascader(id="programmatic", options=WORLD_OPTIONS, placeholder="Driven by buttons..."),
                value_out("programmatic-out"),
            ),
            section(
                "3-level tree with disabled leaf (Juice)",
                "Electronics → Computers / Phones / Audio, Clothing, Food & Drink.",
                dmc.Grid(
                    [
                        dmc.GridCol(
                            [
                                dmc.Text("Single-select", fw=600, size="sm", mb=4),
                                Cascader(id="products-single", options=PRODUCT_OPTIONS, placeholder="Select product..."),
                                value_out("products-single-out"),
                            ],
                            span=6,
                        ),
                        dmc.GridCol(
                            [
                                dmc.Text("Multi-select", fw=600, size="sm", mb=4),
                                Cascader(
                                    id="products-multi",
                                    options=PRODUCT_OPTIONS,
                                    multi=True,
                                    placeholder="Select products...",
                                ),
                                value_out("products-multi-out"),
                            ],
                            span=6,
                        ),
                    ]
                ),
            ),
            section(
                "maxHeight=150px",
                "Each column scrolls independently within the constrained panel height.",
                Cascader(id="maxheight", options=WORLD_OPTIONS, multi=True, maxHeight=150),
            ),
            section(
                "Stress test — wide tree (10 × 10 × 10 = 1 000 leaves)",
                None,
                dmc.Grid(
                    [
                        dmc.GridCol(
                            [
                                dmc.Text("Single-select", fw=600, size="sm", mb=4),
                                Cascader(id="stress-single", options=STRESS_OPTIONS, placeholder="Select item..."),
                                value_out("stress-single-out"),
                            ],
                            span=6,
                        ),
                        dmc.GridCol(
                            [
                                dmc.Text("Multi-select", fw=600, size="sm", mb=4),
                                Cascader(id="stress-multi", options=STRESS_OPTIONS, multi=True, placeholder="Select items..."),
                                value_out("stress-multi-out"),
                            ],
                            span=6,
                        ),
                    ]
                ),
            ),
            section(
                "Stress test — deep tree (5 levels, ~3 000 leaves)",
                None,
                dmc.Grid(
                    [
                        dmc.GridCol(
                            [
                                dmc.Text("Single-select", fw=600, size="sm", mb=4),
                                Cascader(id="deep-single", options=DEEP_OPTIONS, placeholder="Select leaf..."),
                                value_out("deep-single-out"),
                            ],
                            span=6,
                        ),
                        dmc.GridCol(
                            [
                                dmc.Text("Multi-select", fw=600, size="sm", mb=4),
                                Cascader(id="deep-multi", options=DEEP_OPTIONS, multi=True, placeholder="Select leaves..."),
                                value_out("deep-multi-out"),
                            ],
                            span=6,
                        ),
                    ]
                ),
            ),
            html.Div(style={"height": "200px"}),
        ],
        size="lg",
        py="xl",
    ),
    defaultColorScheme="light",
)


@app.callback(Output("single-out", "children"), Input("single", "value"))
def show_single(v):
    return f"value: {v}"


@app.callback(Output("single-preseeded-out", "children"), Input("single-preseeded", "value"))
def show_single_preseeded(v):
    return f"value: {v}"


@app.callback(Output("multi-out", "children"), Input("multi", "value"))
def show_multi(v):
    return f"value: {sorted(v or [])}"


@app.callback(Output("multi-preseeded-out", "children"), Input("multi-preseeded", "value"))
def show_multi_preseeded(v):
    return f"value: {sorted(v or [])}"


@app.callback(
    Output("programmatic", "value"),
    Input("btn-japan", "n_clicks"),
    Input("btn-france", "n_clicks"),
    Input("btn-clear", "n_clicks"),
    prevent_initial_call=True,
)
def set_programmatic(_j, _f, _c):
    if ctx.triggered_id == "btn-japan":
        return "japan"
    if ctx.triggered_id == "btn-france":
        return "france"
    return None


@app.callback(Output("programmatic-out", "children"), Input("programmatic", "value"))
def show_programmatic(v):
    return f"value: {v}"


@app.callback(Output("products-single-out", "children"), Input("products-single", "value"))
def show_products_single(v):
    return f"value: {v}"


@app.callback(Output("products-multi-out", "children"), Input("products-multi", "value"))
def show_products_multi(v):
    return f"value: {sorted(v or [])}"


@app.callback(Output("stress-single-out", "children"), Input("stress-single", "value"))
def show_stress_single(v):
    return f"value: {v}"


@app.callback(Output("stress-multi-out", "children"), Input("stress-multi", "value"))
def show_stress_multi(v):
    sel = v or []
    preview = sorted(sel)[:5]
    suffix = "..." if len(sel) > 5 else ""
    return f"{len(sel)} selected — {preview}{suffix}"


@app.callback(Output("deep-single-out", "children"), Input("deep-single", "value"))
def show_deep_single(v):
    return f"value: {v}"


@app.callback(Output("deep-multi-out", "children"), Input("deep-multi", "value"))
def show_deep_multi(v):
    sel = v or []
    preview = sorted(sel)[:5]
    suffix = "..." if len(sel) > 5 else ""
    return f"{len(sel)} selected — {preview}{suffix}"


if __name__ == "__main__":
    app.run(debug=True)
