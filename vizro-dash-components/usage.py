"""Usage demo for vizro_dash_components — Cascade vs dcc.Dropdown / dbc.Checklist comparison."""

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import Dash, Input, Output, ctx, dcc, html
from vizro_dash_components import Cascade

app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)

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

CHECKLIST_OPTIONS = [o["label"] for o in FLAT_OPTIONS[:8]]

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

app.layout = dmc.MantineProvider(
    dmc.Container(
        [
            dmc.Group(
                [
                    dmc.Title("Cascade vs dcc.Dropdown / dbc.Checklist", order=1),
                    dmc.ColorSchemeToggle(
                        lightIcon=html.Span("\u2600", style={"fontSize": 20}),
                        darkIcon=html.Span("\u263e", style={"fontSize": 20}),
                        size="lg",
                    ),
                ],
                justify="space-between",
                align="center",
                mb="md",
            ),
            dmc.Divider(mb="md"),
            dmc.Title("Direct comparison \u2014 single-select", order=2, mb="xs"),
            dmc.Text(
                "All three side by side. Target: identical trigger height, font, border, focus ring.",
                c="dimmed",
                size="sm",
                mb="sm",
            ),
            dmc.Grid(
                [
                    dmc.GridCol(
                        [
                            dmc.Text("dcc.Dropdown", fw=600, size="sm", mb=4),
                            dcc.Dropdown(
                                id="dcc-single",
                                options=FLAT_OPTIONS,
                                placeholder="Select a country...",
                                clearable=True,
                            ),
                            dmc.Text(id="dcc-single-out", size="xs", c="dimmed", mt=4),
                        ],
                        span=4,
                    ),
                    dmc.GridCol(
                        [
                            dmc.Text("Cascade", fw=600, size="sm", mb=4),
                            Cascade(
                                id="cascade-cmp-single",
                                options=WORLD_OPTIONS,
                                placeholder="Select a country...",
                            ),
                            dmc.Text(id="cascade-single-out", size="xs", c="dimmed", mt=4),
                        ],
                        span=4,
                    ),
                    dmc.GridCol(
                        [
                            dmc.Text("dcc.Dropdown (disabled)", fw=600, size="sm", mb=4),
                            dcc.Dropdown(
                                id="dcc-single-disabled",
                                options=FLAT_OPTIONS,
                                value="japan",
                                disabled=True,
                            ),
                        ],
                        span=4,
                    ),
                ],
                mb="md",
            ),
            dmc.Divider(my="xl"),
            dmc.Title("Direct comparison \u2014 multi-select", order=2, mb="xs"),
            dmc.Text(
                "Count badge, Select all, clear. Target: same single-line trigger height as dcc.Dropdown.",
                c="dimmed",
                size="sm",
                mb="sm",
            ),
            dmc.Grid(
                [
                    dmc.GridCol(
                        [
                            dmc.Text("dcc.Dropdown multi", fw=600, size="sm", mb=4),
                            dcc.Dropdown(
                                id="dcc-multi",
                                options=FLAT_OPTIONS,
                                multi=True,
                                placeholder="Select countries...",
                            ),
                            dmc.Text(id="dcc-multi-out", size="xs", c="dimmed", mt=4),
                        ],
                        span=6,
                    ),
                    dmc.GridCol(
                        [
                            dmc.Text("Cascade multi", fw=600, size="sm", mb=4),
                            Cascade(
                                id="cascade-cmp-multi",
                                options=WORLD_OPTIONS,
                                multi=True,
                                placeholder="Select countries...",
                            ),
                            dmc.Text(id="cascade-multi-out", size="xs", c="dimmed", mt=4),
                        ],
                        span=6,
                    ),
                ],
                mb="md",
            ),
            dmc.Divider(my="xl"),
            dmc.Title("Checklist comparison", order=2, mb="xs"),
            dmc.Text(
                "dbc.Checklist vs Cascade multi panel. Target: identical checkbox, hover, font weight on selected.",
                c="dimmed",
                size="sm",
                mb="sm",
            ),
            dmc.Grid(
                [
                    dmc.GridCol(
                        [
                            dmc.Text("dbc.Checklist", fw=600, size="sm", mb=4),
                            dbc.Checklist(id="dbc-checklist", options=CHECKLIST_OPTIONS, value=[]),
                        ],
                        span=6,
                    ),
                    dmc.GridCol(
                        [
                            dmc.Text("Cascade multi (open to compare checkboxes)", fw=600, size="sm", mb=4),
                            Cascade(
                                id="cascade-cmp-checklist",
                                options=WORLD_OPTIONS,
                                multi=True,
                                placeholder="Open to compare checkboxes...",
                            ),
                        ],
                        span=6,
                    ),
                ],
                mb="md",
            ),
            dmc.Divider(my="xl"),
            dmc.Title("Pre-seeded single value", order=2, mb="xs"),
            dmc.Grid(
                [
                    dmc.GridCol(
                        [
                            dmc.Text("dcc.Dropdown value='japan'", fw=600, size="sm", mb=4),
                            dcc.Dropdown(id="dcc-preseeded", options=FLAT_OPTIONS, value="japan"),
                        ],
                        span=6,
                    ),
                    dmc.GridCol(
                        [
                            dmc.Text("Cascade value='japan'", fw=600, size="sm", mb=4),
                            Cascade(id="cascade-preseeded", options=WORLD_OPTIONS, value="japan"),
                        ],
                        span=6,
                    ),
                ],
            ),
            dmc.Divider(my="xl"),
            dmc.Title("Pre-seeded multi \u2014 japan + france + germany", order=2, mb="xs"),
            dmc.Grid(
                [
                    dmc.GridCol(
                        [
                            dmc.Text("dcc.Dropdown multi", fw=600, size="sm", mb=4),
                            dcc.Dropdown(
                                id="dcc-preseeded-multi",
                                options=FLAT_OPTIONS,
                                multi=True,
                                value=["japan", "france", "germany"],
                            ),
                        ],
                        span=6,
                    ),
                    dmc.GridCol(
                        [
                            dmc.Text("Cascade multi", fw=600, size="sm", mb=4),
                            Cascade(
                                id="cascade-preseeded-multi",
                                options=WORLD_OPTIONS,
                                multi=True,
                                value=["japan", "france", "germany"],
                            ),
                        ],
                        span=6,
                    ),
                ],
            ),
            dmc.Divider(my="xl"),
            dmc.Title("searchable=False, clearable=False", order=2, mb="xs"),
            dmc.Grid(
                [
                    dmc.GridCol(
                        [
                            dmc.Text("dcc.Dropdown", fw=600, size="sm", mb=4),
                            dcc.Dropdown(
                                id="dcc-no-search",
                                options=FLAT_OPTIONS,
                                searchable=False,
                                clearable=False,
                                placeholder="No search/clear...",
                            ),
                        ],
                        span=6,
                    ),
                    dmc.GridCol(
                        [
                            dmc.Text("Cascade", fw=600, size="sm", mb=4),
                            Cascade(
                                id="cascade-no-search",
                                options=WORLD_OPTIONS,
                                searchable=False,
                                clearable=False,
                                placeholder="No search/clear...",
                            ),
                        ],
                        span=6,
                    ),
                ],
            ),
            dmc.Divider(my="xl"),
            dmc.Title("disabled=True", order=2, mb="xs"),
            dmc.Grid(
                [
                    dmc.GridCol(
                        [
                            dmc.Text("dcc.Dropdown disabled (no value)", fw=600, size="sm", mb=4),
                            dcc.Dropdown(id="dcc-disabled", options=FLAT_OPTIONS, disabled=True),
                        ],
                        span=3,
                    ),
                    dmc.GridCol(
                        [
                            dmc.Text("dcc.Dropdown disabled (with value)", fw=600, size="sm", mb=4),
                            dcc.Dropdown(
                                id="dcc-disabled-val",
                                options=FLAT_OPTIONS,
                                value="japan",
                                disabled=True,
                            ),
                        ],
                        span=3,
                    ),
                    dmc.GridCol(
                        [
                            dmc.Text("Cascade disabled (no value)", fw=600, size="sm", mb=4),
                            Cascade(id="cascade-disabled", options=WORLD_OPTIONS, disabled=True),
                        ],
                        span=3,
                    ),
                    dmc.GridCol(
                        [
                            dmc.Text("Cascade disabled (with value)", fw=600, size="sm", mb=4),
                            Cascade(id="cascade-disabled-val", options=WORLD_OPTIONS, disabled=True, value="japan"),
                        ],
                        span=3,
                    ),
                ],
            ),
            dmc.Divider(my="xl"),
            dmc.Title("Programmatic value update", order=2, mb="xs"),
            dmc.Text("Buttons drive both components simultaneously.", c="dimmed", size="sm", mb="sm"),
            dmc.Group(
                [
                    dmc.Button("Set Japan", id="btn-japan", variant="outline", size="sm"),
                    dmc.Button("Set France", id="btn-france", variant="outline", size="sm"),
                    dmc.Button("Clear", id="btn-clear", variant="outline", size="sm", color="red"),
                ],
                mb="sm",
            ),
            dmc.Grid(
                [
                    dmc.GridCol(
                        [
                            dmc.Text("dcc.Dropdown", fw=600, size="sm", mb=4),
                            dcc.Dropdown(
                                id="dcc-programmatic",
                                options=FLAT_OPTIONS,
                                placeholder="Driven by buttons...",
                            ),
                        ],
                        span=6,
                    ),
                    dmc.GridCol(
                        [
                            dmc.Text("Cascade", fw=600, size="sm", mb=4),
                            Cascade(
                                id="cascade-programmatic",
                                options=WORLD_OPTIONS,
                                placeholder="Driven by buttons...",
                            ),
                        ],
                        span=6,
                    ),
                ],
            ),
            dmc.Divider(my="xl"),
            dmc.Title("Products tree \u2014 3 levels with disabled leaf (Juice)", order=2, mb="xs"),
            dmc.Grid(
                [
                    dmc.GridCol(
                        Cascade(
                            id="cascade-products-single",
                            options=PRODUCT_OPTIONS,
                            placeholder="Single-select...",
                        ),
                        span=6,
                    ),
                    dmc.GridCol(
                        Cascade(
                            id="cascade-products-multi",
                            options=PRODUCT_OPTIONS,
                            multi=True,
                            placeholder="Multi-select...",
                        ),
                        span=6,
                    ),
                ],
            ),
            dmc.Divider(my="xl"),
            dmc.Title("maxHeight=150px \u2014 each column scrolls independently", order=2, mb="xs"),
            Cascade(id="cascade-maxheight", options=WORLD_OPTIONS, multi=True, maxHeight=150),
            html.Div(style={"height": "200px"}),
        ],
        size="lg",
        py="xl",
    ),
    defaultColorScheme="light",
)


@app.callback(Output("dcc-single-out", "children"), Input("dcc-single", "value"))
def show_dcc_single(value):
    return f"value: {value}"


@app.callback(Output("cascade-single-out", "children"), Input("cascade-cmp-single", "value"))
def show_cascade_single(value):
    return f"value: {value}"


@app.callback(Output("dcc-multi-out", "children"), Input("dcc-multi", "value"))
def show_dcc_multi(value):
    return f"value: {sorted(value or [])}"


@app.callback(Output("cascade-multi-out", "children"), Input("cascade-cmp-multi", "value"))
def show_cascade_multi(value):
    return f"value: {sorted(value or [])}"


@app.callback(
    Output("dcc-programmatic", "value"),
    Output("cascade-programmatic", "value"),
    Input("btn-japan", "n_clicks"),
    Input("btn-france", "n_clicks"),
    Input("btn-clear", "n_clicks"),
    prevent_initial_call=True,
)
def set_programmatic(_j, _f, _c):
    if ctx.triggered_id == "btn-japan":
        return "japan", "japan"
    if ctx.triggered_id == "btn-france":
        return "france", "france"
    return None, None


if __name__ == "__main__":
    app.run(debug=True)
