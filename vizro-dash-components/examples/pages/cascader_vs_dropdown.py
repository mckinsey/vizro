"""Side-by-side vdc.Cascader vs dcc.Dropdown: visual comparisons and stress test."""

# ruff: noqa: D103

from __future__ import annotations

import dash
import dash_mantine_components as dmc
import vizro_dash_components as vdc
from dash import Input, Output, callback, dcc, html

# name= required: Dash default title-cases only the first character ("Vdc.cascader vs dropdown").
dash.register_page(
    __name__,
    name="vdc.Cascader vs dcc.Dropdown",
    title="Comparison: vdc.Cascader vs dcc.Dropdown",
)

# --- Visual comparison datasets (small, readable) ---

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

# Explicit list-of-dicts shape (same as dcc.Dropdown-style option nodes)
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


def count_leaves_dict_tree(tree: dict) -> int:
    n = 0
    for countries in tree.values():
        if isinstance(countries, dict):
            for cities in countries.values():
                if isinstance(cities, list):
                    n += len(cities)
    return n


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
    """Leaf-only options; path labels for the flat dropdown."""
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


def count_leaves_nested(node: dict | list) -> int:
    """Count scalar leaves in a nested dict-of-dicts-...-of-list tree."""
    if isinstance(node, list):
        return len(node)
    return sum(count_leaves_nested(v) for v in node.values())


def flatten_nested_dict_tree(tree: dict, path: tuple[str, ...] = ()) -> list[dict]:
    """Flat dropdown options: full path label, leaf value (same as flatten_dict_tree shape)."""
    out: list[dict] = []
    for key, val in tree.items():
        here = (*path, key)
        if isinstance(val, list):
            out.extend({"label": " / ".join((*here, str(item))), "value": item} for item in val)
        else:
            out.extend(flatten_nested_dict_tree(val, here))
    return out


# --- Stress dataset: 5 nested levels, then terminal lists; uneven fan-out; ≤10k leaves ---

STRESS_DEPTH = 5
STRESS_BRANCHES = (10, 2, 8, 5, 6)
STRESS_LEAVES_PER_TERMINAL = 2


def build_stress_tree() -> dict:
    def node(level: int, path: tuple[int, ...]) -> dict | list[str]:
        if level >= STRESS_DEPTH:
            p = ".".join(str(i) for i in path)
            return [f"item-{p}-{k}" for k in range(STRESS_LEAVES_PER_TERMINAL)]
        n_br = STRESS_BRANCHES[level]
        out: dict = {}
        for i in range(n_br):
            sub = (*path, i)
            key = f"lvl{level + 1}-{'.'.join(str(j) for j in sub)}"
            out[key] = node(level + 1, sub)
        return out

    return node(0, ())


STRESS_TREE = build_stress_tree()
STRESS_LEAVES = count_leaves_nested(STRESS_TREE)
STRESS_FLAT = flatten_nested_dict_tree(STRESS_TREE)

LOCATIONS_FLAT = flatten_dict_tree(LOCATIONS)
PRODUCTS_FLAT = flatten_dict_tree(PRODUCTS)
ORG_FLAT = flatten_explicit_nodes(ORG_TREE)

_INLINE_CODE_STYLE = {
    "fontFamily": "var(--mantine-font-family-monospace, ui-monospace, monospace)",
    "fontSize": "0.88em",
}

COLUMN_STYLE = {
    "flex": "1 1 380px",
    "minWidth": "360px",
    "maxWidth": "520px",
}


def compare_column(title: str, component, output_id: str) -> html.Div:
    return html.Div(
        [
            dmc.Title(title, order=4, mb="xs"),
            component,
            dmc.Text(id=output_id, size="sm", c="dimmed", mt="sm"),
        ],
        style=COLUMN_STYLE,
    )


def side_by_side(*columns: html.Div) -> html.Div:
    return html.Div(
        list(columns),
        style={"display": "flex", "flexWrap": "wrap", "gap": "2rem", "alignItems": "flex-start"},
    )


layout = html.Div(
    [
        dmc.Text(
            [
                "Same leaf values everywhere: hierarchical ",
                html.Code("options", style=_INLINE_CODE_STYLE),
                " for vdc.Cascader vs a flat ",
                html.Code("options", style=_INLINE_CODE_STYLE),
                " list for dcc.Dropdown. Two sections below — quick visual comparisons, then a large stress test.",
            ],
            c="dimmed",
            size="sm",
            mb="lg",
            span=True,
        ),
        # --- Visual comparison ---
        dmc.Paper(
            [
                dmc.Title("Visual comparison", order=3, mb="xs"),
                dmc.Text(
                    "Small datasets to compare layout, typography, search, and interaction side by side.",
                    c="dimmed",
                    size="sm",
                    mb="lg",
                ),
                dmc.Title("Cities (single-select)", order=4, mb="sm"),
                side_by_side(
                    compare_column(
                        "vdc.Cascader",
                        vdc.Cascader(
                            id="vis-cascade-cities",
                            options=LOCATIONS,
                            placeholder="Pick a city…",
                            searchable=True,
                            clearable=True,
                            maxHeight=280,
                        ),
                        "vis-cascade-cities-out",
                    ),
                    compare_column(
                        "dcc.Dropdown",
                        dcc.Dropdown(
                            id="vis-dropdown-cities",
                            options=LOCATIONS_FLAT,
                            placeholder="Search cities…",
                            searchable=True,
                            clearable=True,
                            maxHeight=280,
                            style={"width": "100%"},
                        ),
                        "vis-dropdown-cities-out",
                    ),
                ),
                dmc.Divider(my="xl"),
                dmc.Title("Products (multi-select)", order=4, mb="sm"),
                side_by_side(
                    compare_column(
                        "vdc.Cascader",
                        vdc.Cascader(
                            id="vis-cascade-products",
                            options=PRODUCTS,
                            placeholder="Pick products…",
                            multi=True,
                            searchable=True,
                            clearable=True,
                            maxHeight=280,
                            debounce=True,
                        ),
                        "vis-cascade-products-out",
                    ),
                    compare_column(
                        "dcc.Dropdown",
                        dcc.Dropdown(
                            id="vis-dropdown-products",
                            options=PRODUCTS_FLAT,
                            placeholder="Search products…",
                            multi=True,
                            searchable=True,
                            clearable=True,
                            maxHeight=280,
                            style={"width": "100%"},
                        ),
                        "vis-dropdown-products-out",
                    ),
                ),
                dmc.Divider(my="xl"),
                dmc.Title(
                    [
                        "Explicit ",
                        html.Code("{label, value, children}", style=_INLINE_CODE_STYLE),
                        " tree (single-select)",
                    ],
                    order=4,
                    mb="sm",
                ),
                dmc.Text(
                    [
                        "vdc.Cascader ",
                        html.Code("options", style=_INLINE_CODE_STYLE),
                        " as a list of objects; Dropdown still uses the same leaf ",
                        html.Code("value", style=_INLINE_CODE_STYLE),
                        " strings.",
                    ],
                    size="xs",
                    c="dimmed",
                    mb="sm",
                    span=True,
                ),
                side_by_side(
                    compare_column(
                        "vdc.Cascader",
                        vdc.Cascader(
                            id="vis-cascade-explicit",
                            options=ORG_TREE,
                            placeholder="Pick a person…",
                            searchable=True,
                            clearable=True,
                            maxHeight=280,
                        ),
                        "vis-cascade-explicit-out",
                    ),
                    compare_column(
                        "dcc.Dropdown",
                        dcc.Dropdown(
                            id="vis-dropdown-explicit",
                            options=ORG_FLAT,
                            placeholder="Search people…",
                            searchable=True,
                            clearable=True,
                            maxHeight=280,
                            style={"width": "100%"},
                        ),
                        "vis-dropdown-explicit-out",
                    ),
                ),
            ],
            p="lg",
            withBorder=True,
            mb="xl",
        ),
        # --- Stress test ---
        dmc.Paper(
            [
                dmc.Title("Stress test", order=3, mb="xs"),
                dmc.Text(
                    f"Large synthetic tree: {STRESS_DEPTH} levels deep (nested groups), branching "
                    f"{STRESS_BRANCHES}, {STRESS_LEAVES_PER_TERMINAL} leaves per terminal → "
                    f"{STRESS_LEAVES:,} leaf values. Use for scroll performance, search, and panel behavior.",
                    c="dimmed",
                    size="sm",
                    mb="lg",
                ),
                dmc.Title("Single-select", order=4, mb="sm"),
                side_by_side(
                    compare_column(
                        "vdc.Cascader",
                        vdc.Cascader(
                            id="stress-cascade-single",
                            options=STRESS_TREE,
                            placeholder="Open panels…",
                            searchable=True,
                            clearable=True,
                            maxHeight=360,
                        ),
                        "stress-cascade-single-out",
                    ),
                    compare_column(
                        "dcc.Dropdown",
                        dcc.Dropdown(
                            id="stress-dropdown-single",
                            options=STRESS_FLAT,
                            placeholder="Search flat list…",
                            searchable=True,
                            clearable=True,
                            maxHeight=360,
                            style={"width": "100%"},
                        ),
                        "stress-dropdown-single-out",
                    ),
                ),
                dmc.Divider(my="xl"),
                dmc.Title("Multi-select", order=4, mb="sm"),
                side_by_side(
                    compare_column(
                        "vdc.Cascader",
                        vdc.Cascader(
                            id="stress-cascade-multi",
                            options=STRESS_TREE,
                            placeholder="Multi…",
                            multi=True,
                            searchable=True,
                            clearable=True,
                            maxHeight=360,
                            debounce=True,
                        ),
                        "stress-cascade-multi-out",
                    ),
                    compare_column(
                        "dcc.Dropdown",
                        dcc.Dropdown(
                            id="stress-dropdown-multi",
                            options=STRESS_FLAT,
                            placeholder="Multi flat…",
                            multi=True,
                            searchable=True,
                            clearable=True,
                            maxHeight=360,
                            style={"width": "100%"},
                        ),
                        "stress-dropdown-multi-out",
                    ),
                ),
            ],
            p="lg",
            withBorder=True,
        ),
    ]
)


def _fmt_multi(v):
    return sorted(v) if v else v


@callback(Output("vis-cascade-cities-out", "children"), Input("vis-cascade-cities", "value"))
def _vis_cities_cas(v):
    return f"Cascader: {v!r}"


@callback(Output("vis-dropdown-cities-out", "children"), Input("vis-dropdown-cities", "value"))
def _vis_cities_dd(v):
    return f"Dropdown: {v!r}"


@callback(Output("vis-cascade-products-out", "children"), Input("vis-cascade-products", "value"))
def _vis_prod_cas(v):
    return f"Cascader: {_fmt_multi(v)!r}"


@callback(Output("vis-dropdown-products-out", "children"), Input("vis-dropdown-products", "value"))
def _vis_prod_dd(v):
    return f"Dropdown: {_fmt_multi(v)!r}"


@callback(Output("vis-cascade-explicit-out", "children"), Input("vis-cascade-explicit", "value"))
def _vis_exp_cas(v):
    return f"Cascader: {v!r}"


@callback(Output("vis-dropdown-explicit-out", "children"), Input("vis-dropdown-explicit", "value"))
def _vis_exp_dd(v):
    return f"Dropdown: {v!r}"


@callback(Output("stress-cascade-single-out", "children"), Input("stress-cascade-single", "value"))
def _stress_cas_single(v):
    return f"Cascader: {v!r}"


@callback(Output("stress-dropdown-single-out", "children"), Input("stress-dropdown-single", "value"))
def _stress_dd_single(v):
    return f"Dropdown: {v!r}"


@callback(Output("stress-cascade-multi-out", "children"), Input("stress-cascade-multi", "value"))
def _stress_cas_multi(v):
    return f"Cascader: {_fmt_multi(v)!r}"


@callback(Output("stress-dropdown-multi-out", "children"), Input("stress-dropdown-multi", "value"))
def _stress_dd_multi(v):
    return f"Dropdown: {_fmt_multi(v)!r}"
