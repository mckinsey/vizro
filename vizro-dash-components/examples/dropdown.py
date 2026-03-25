"""QA comparison app for dcc.Dropdown — mirrors cascader.py section-for-section."""

import dash_mantine_components as dmc
from dash import Dash, Input, Output, ctx, dcc, html

FLAT_OPTIONS = [
    {"label": "Japan", "value": "japan"},
    {"label": "China", "value": "china"},
    {"label": "South Korea", "value": "south_korea"},
    {"label": "India", "value": "india"},
    {"label": "Pakistan", "value": "pakistan"},
    {"label": "Bangladesh", "value": "bangladesh"},
    {"label": "Thailand", "value": "thailand"},
    {"label": "Vietnam", "value": "vietnam"},
    {"label": "Indonesia", "value": "indonesia"},
    {"label": "France", "value": "france"},
    {"label": "Germany", "value": "germany"},
    {"label": "Netherlands", "value": "netherlands"},
    {"label": "Sweden", "value": "sweden"},
    {"label": "Norway", "value": "norway"},
    {"label": "Denmark", "value": "denmark"},
    {"label": "USA", "value": "usa"},
    {"label": "Canada", "value": "canada"},
    {"label": "Mexico", "value": "mexico"},
    {"label": "Brazil", "value": "brazil"},
    {"label": "Argentina", "value": "argentina"},
]

PRODUCT_OPTIONS_FLAT = [
    {"label": "Laptops", "value": "laptops"},
    {"label": "Desktops", "value": "desktops"},
    {"label": "Tablets", "value": "tablets"},
    {"label": "Smartphones", "value": "smartphones"},
    {"label": "Feature Phones", "value": "feature_phones"},
    {"label": "Headphones", "value": "headphones"},
    {"label": "Speakers", "value": "speakers"},
    {"label": "Earbuds", "value": "earbuds"},
    {"label": "Shirts (M)", "value": "mens_shirts"},
    {"label": "Trousers (M)", "value": "mens_trousers"},
    {"label": "Shoes (M)", "value": "mens_shoes"},
    {"label": "Dresses (W)", "value": "womens_dresses"},
    {"label": "Tops (W)", "value": "womens_tops"},
    {"label": "Shoes (W)", "value": "womens_shoes"},
    {"label": "Coffee", "value": "coffee"},
    {"label": "Tea", "value": "tea"},
    {"label": "Juice", "value": "juice", "disabled": True},
    {"label": "Chips", "value": "chips"},
    {"label": "Chocolate", "value": "chocolate"},
    {"label": "Nuts", "value": "nuts"},
]

STRESS_OPTIONS = [{"label": f"Item {i:03d}", "value": f"item_{i:03d}"} for i in range(1000)]
DEEP_OPTIONS = [{"label": f"Leaf {i:04d}", "value": f"leaf_{i:04d}"} for i in range(3125)]


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
                    dmc.Title("dcc.Dropdown — QA reference", order=1),
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
                "Value set on click, panel closes, clear button resets to null.",
                dmc.Grid(
                    [
                        dmc.GridCol(
                            [
                                dmc.Text("Default", fw=600, size="sm", mb=4),
                                dcc.Dropdown(id="single", options=FLAT_OPTIONS, placeholder="Select a country..."),
                                value_out("single-out"),
                            ],
                            span=6,
                        ),
                        dmc.GridCol(
                            [
                                dmc.Text("Pre-seeded: value='japan'", fw=600, size="sm", mb=4),
                                dcc.Dropdown(id="single-preseeded", options=FLAT_OPTIONS, value="japan"),
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
                                dcc.Dropdown(id="multi", options=FLAT_OPTIONS, multi=True, placeholder="Select countries..."),
                                value_out("multi-out"),
                            ],
                            span=6,
                        ),
                        dmc.GridCol(
                            [
                                dmc.Text("Pre-seeded: japan + france + germany", fw=600, size="sm", mb=4),
                                dcc.Dropdown(
                                    id="multi-preseeded",
                                    options=FLAT_OPTIONS,
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
                                dcc.Dropdown(
                                    id="no-search-single",
                                    options=FLAT_OPTIONS,
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
                                dcc.Dropdown(
                                    id="no-search-multi",
                                    options=FLAT_OPTIONS,
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
                                dcc.Dropdown(id="disabled-empty", options=FLAT_OPTIONS, disabled=True),
                            ],
                            span=3,
                        ),
                        dmc.GridCol(
                            [
                                dmc.Text("With value", fw=600, size="sm", mb=4),
                                dcc.Dropdown(id="disabled-val", options=FLAT_OPTIONS, disabled=True, value="japan"),
                            ],
                            span=3,
                        ),
                        dmc.GridCol(
                            [
                                dmc.Text("Multi with value", fw=600, size="sm", mb=4),
                                dcc.Dropdown(
                                    id="disabled-multi",
                                    options=FLAT_OPTIONS,
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
                "Buttons drive the Dropdown value from a callback.",
                dmc.Group(
                    [
                        dmc.Button("Set Japan", id="btn-japan", variant="outline", size="sm"),
                        dmc.Button("Set France", id="btn-france", variant="outline", size="sm"),
                        dmc.Button("Clear", id="btn-clear", variant="outline", size="sm", color="red"),
                    ],
                    mb="sm",
                ),
                dcc.Dropdown(id="programmatic", options=FLAT_OPTIONS, placeholder="Driven by buttons..."),
                value_out("programmatic-out"),
            ),
            section(
                "Products (flat) with disabled leaf (Juice)",
                "Flat equivalent of the 3-level product tree.",
                dmc.Grid(
                    [
                        dmc.GridCol(
                            [
                                dmc.Text("Single-select", fw=600, size="sm", mb=4),
                                dcc.Dropdown(id="products-single", options=PRODUCT_OPTIONS_FLAT, placeholder="Select product..."),
                                value_out("products-single-out"),
                            ],
                            span=6,
                        ),
                        dmc.GridCol(
                            [
                                dmc.Text("Multi-select", fw=600, size="sm", mb=4),
                                dcc.Dropdown(
                                    id="products-multi",
                                    options=PRODUCT_OPTIONS_FLAT,
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
                None,
                dcc.Dropdown(id="maxheight", options=FLAT_OPTIONS, multi=True, maxHeight=150),
            ),
            section(
                "Stress test — 1 000 options",
                None,
                dmc.Grid(
                    [
                        dmc.GridCol(
                            [
                                dmc.Text("Single-select", fw=600, size="sm", mb=4),
                                dcc.Dropdown(id="stress-single", options=STRESS_OPTIONS, placeholder="Select item..."),
                                value_out("stress-single-out"),
                            ],
                            span=6,
                        ),
                        dmc.GridCol(
                            [
                                dmc.Text("Multi-select", fw=600, size="sm", mb=4),
                                dcc.Dropdown(id="stress-multi", options=STRESS_OPTIONS, multi=True, placeholder="Select items..."),
                                value_out("stress-multi-out"),
                            ],
                            span=6,
                        ),
                    ]
                ),
            ),
            section(
                "Stress test — 3 125 options",
                None,
                dmc.Grid(
                    [
                        dmc.GridCol(
                            [
                                dmc.Text("Single-select", fw=600, size="sm", mb=4),
                                dcc.Dropdown(id="deep-single", options=DEEP_OPTIONS, placeholder="Select..."),
                                value_out("deep-single-out"),
                            ],
                            span=6,
                        ),
                        dmc.GridCol(
                            [
                                dmc.Text("Multi-select", fw=600, size="sm", mb=4),
                                dcc.Dropdown(id="deep-multi", options=DEEP_OPTIONS, multi=True, placeholder="Select..."),
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
    app.run(debug=True, port=8053)
