"""Side-by-side vdc.Cascader vs dcc.Dropdown: visual comparisons."""

# ruff: noqa: D103

from __future__ import annotations

import dash
import dash_mantine_components as dmc
import vizro_dash_components as vdc
from dash import Input, Output, callback, dcc, html

dash.register_page(
    __name__,
    name="vdc.Cascader vs dcc.Dropdown",
    title="Comparison: vdc.Cascader vs dcc.Dropdown",
)

LOCATIONS = {
    "Asia": {
        "Japan": ["Tokyo", "Osaka", "Kyoto"],
        "China": ["Beijing", "Shanghai"],
    },
    "Europe": {
        "France": ["Paris", "Lyon"],
        "Germany": ["Berlin", "Munich"],
    },
}

PRODUCTS = {
    "Electronics": {
        "Computers": ["Laptops", "Desktops"],
        "Phones": ["Smartphones", "Feature phones"],
    },
    "Clothing": {
        "Men's": ["Shirts", "Shoes"],
        "Women's": ["Dresses", "Tops"],
    },
}

ORG_TREE = [
    {
        "label": "Engineering",
        "value": "eng",
        "children": [
            {"label": "Alice", "value": "alice"},
            {"label": "Bob", "value": "bob"},
        ],
    },
    {
        "label": "Sales",
        "value": "sales",
        "children": [
            {"label": "Carol", "value": "carol"},
            {"label": "Dan", "value": "dan"},
        ],
    },
]


def flatten_dict_tree(tree: dict) -> list[dict]:
    return [
        {"label": f"{region} / {country} / {city}", "value": city}
        for region, countries in tree.items()
        if isinstance(countries, dict)
        for country, cities in countries.items()
        if isinstance(cities, list)
        for city in cities
    ]


def flatten_explicit_nodes(nodes: list[dict]) -> list[dict]:
    out: list[dict] = []

    def walk(node: dict, path: list[str]) -> None:
        label = node["label"]
        value = node["value"]
        kids = node.get("children")
        segments = [*path, label]
        if kids:
            for child in kids:
                walk(child, segments)
        else:
            out.append({"label": " / ".join(segments), "value": value})

    for root in nodes:
        walk(root, [])
    return out


LOCATIONS_FLAT = flatten_dict_tree(LOCATIONS)
PRODUCTS_FLAT = flatten_dict_tree(PRODUCTS)
ORG_FLAT = flatten_explicit_nodes(ORG_TREE)

_CODE = {"fontFamily": "var(--mantine-font-family-monospace, ui-monospace, monospace)", "fontSize": "0.88em"}
_COL = {"flex": "1 1 380px", "minWidth": "360px", "maxWidth": "520px"}


def _pair(title: str, left, right, left_out: str, right_out: str) -> html.Div:
    return html.Div(
        [
            dmc.Title(title, order=4, mb="sm"),
            html.Div(
                [
                    html.Div(
                        [
                            dmc.Title("vdc.Cascader", order=5, mb="xs"),
                            left,
                            dmc.Text(id=left_out, size="sm", c="dimmed", mt="sm"),
                        ],
                        style=_COL,
                    ),
                    html.Div(
                        [
                            dmc.Title("dcc.Dropdown", order=5, mb="xs"),
                            right,
                            dmc.Text(id=right_out, size="sm", c="dimmed", mt="sm"),
                        ],
                        style=_COL,
                    ),
                ],
                style={"display": "flex", "flexWrap": "wrap", "gap": "2rem", "alignItems": "flex-start"},
            ),
        ]
    )


layout = html.Div(
    [
        dmc.Text(
            [
                "Same leaf values: hierarchical ",
                html.Code("options", style=_CODE),
                " for Cascader vs a flat list for Dropdown.",
            ],
            c="dimmed",
            size="sm",
            mb="lg",
            span=True,
        ),
        dmc.Title("Visual comparison", order=3, mb="xs"),
        dmc.Text(
            "Small datasets: layout, search, and interaction.",
            c="dimmed",
            size="sm",
            mb="lg",
        ),
        _pair(
            "Cities (single-select)",
            vdc.Cascader(
                id="city-cascade",
                options=LOCATIONS,
                placeholder="Pick a city…",
                searchable=True,
                clearable=True,
                maxHeight=280,
            ),
            dcc.Dropdown(
                id="city-dropdown",
                options=LOCATIONS_FLAT,
                placeholder="Search cities…",
                searchable=True,
                clearable=True,
                maxHeight=280,
                style={"width": "100%"},
            ),
            "city-cascade-out",
            "city-dropdown-out",
        ),
        dmc.Divider(my="xl"),
        _pair(
            "Products (multi-select)",
            vdc.Cascader(
                id="prod-cascade",
                options=PRODUCTS,
                placeholder="Pick products…",
                multi=True,
                searchable=True,
                clearable=True,
                maxHeight=280,
                debounce=True,
            ),
            dcc.Dropdown(
                id="prod-dropdown",
                options=PRODUCTS_FLAT,
                placeholder="Search products…",
                multi=True,
                searchable=True,
                clearable=True,
                maxHeight=280,
                style={"width": "100%"},
            ),
            "prod-cascade-out",
            "prod-dropdown-out",
        ),
        dmc.Divider(my="xl"),
        _pair(
            "Explicit tree (single-select)",
            vdc.Cascader(
                id="org-cascade",
                options=ORG_TREE,
                placeholder="Pick a person…",
                searchable=True,
                clearable=True,
                maxHeight=280,
            ),
            dcc.Dropdown(
                id="org-dropdown",
                options=ORG_FLAT,
                placeholder="Search people…",
                searchable=True,
                clearable=True,
                maxHeight=280,
                style={"width": "100%"},
            ),
            "org-cascade-out",
            "org-dropdown-out",
        ),
    ]
)


def _fmt_multi(v):
    return sorted(v) if v else v


@callback(Output("city-cascade-out", "children"), Input("city-cascade", "value"))
def _city_cas(v):
    return f"Cascader: {v!r}"


@callback(Output("city-dropdown-out", "children"), Input("city-dropdown", "value"))
def _city_dd(v):
    return f"Dropdown: {v!r}"


@callback(Output("prod-cascade-out", "children"), Input("prod-cascade", "value"))
def _prod_cas(v):
    return f"Cascader: {_fmt_multi(v)!r}"


@callback(Output("prod-dropdown-out", "children"), Input("prod-dropdown", "value"))
def _prod_dd(v):
    return f"Dropdown: {_fmt_multi(v)!r}"


@callback(Output("org-cascade-out", "children"), Input("org-cascade", "value"))
def _org_cas(v):
    return f"Cascader: {v!r}"


@callback(Output("org-dropdown-out", "children"), Input("org-dropdown", "value"))
def _org_dd(v):
    return f"Dropdown: {v!r}"
