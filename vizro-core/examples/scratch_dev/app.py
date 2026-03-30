"""Dev app to try things out."""

import json

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
import vizro_dash_components as vdc
from vizro import Vizro
from vizro.models.types import capture

# --- Data ---

_STRUCTURE = {
    "Electronics": {
        "Phones": ["iPhone 15", "Android", "Pixel 8"],
        "Laptops": ["MacBook", "ThinkPad", "Dell XPS"],
    },
    "Clothing": {
        "Tops": ["Oxford Shirt", "Polo Shirt", "T-Shirt"],
        "Bottoms": ["Jeans", "Chinos", "Shorts"],
    },
    "Food": {
        "Fruit": ["Apple", "Banana", "Orange"],
        "Vegetables": ["Carrot", "Broccoli", "Spinach"],
    },
}

gapminder = px.data.gapminder()
continents = gapminder["continent"].unique().tolist()
GAPMINDER_OPTIONS = {
    continent: gapminder[gapminder["continent"] == continent]["country"].unique().tolist() for continent in continents
}

dummy_df = pd.DataFrame({"category": ["Electronics", "Clothing", "Food"]})
gapminder_2007 = gapminder[gapminder["year"] == 2007].copy()


# --- Custom figures ---


@capture("figure")
def show_selected(data_frame: pd.DataFrame, selected=None):
    """Display selected values as JSON."""
    code = json.dumps(selected, indent=2) if selected is not None else "null"
    return vdc.Markdown(children=f"```json\n{code}\n```")


@capture("graph")
def gapminder_bar(data_frame: pd.DataFrame, countries=None):
    """Bar chart of 2007 gapminder life expectancy, filtered to selected countries."""
    if countries:
        data_frame = data_frame[data_frame["country"].isin(countries)]
    return px.bar(data_frame, x="country", y="lifeExp", color="continent")


# --- Page: Cascader as Parameter ---

page_parameter = vm.Page(
    title="Cascader as Parameter",
    components=[
        vm.Figure(id="figure-products-single", figure=show_selected(data_frame=dummy_df, selected=None)),
        vm.Figure(id="figure-products-multi", figure=show_selected(data_frame=dummy_df, selected=[])),
        vm.Graph(id="graph-gapminder", figure=gapminder_bar(data_frame=gapminder_2007, countries=[])),
    ],
    controls=[
        vm.Parameter(
            targets=["figure-products-single.selected"],
            selector=vm.Cascader(
                options=_STRUCTURE,
                title="Products (Cascader multi=False)",
                multi=False,
            ),
        ),
        vm.Parameter(
            targets=["figure-products-multi.selected"],
            selector=vm.Cascader(
                options=_STRUCTURE,
                title="Products (Cascader multi=True)",
                multi=True,
            ),
        ),
        vm.Parameter(
            targets=["graph-gapminder.countries"],
            selector=vm.Cascader(
                options=GAPMINDER_OPTIONS,
                title="Gapminder countries (Cascader multi=True)",
            ),
        ),
    ],
)

# --- Page: Cascader as Filter vs Dropdown ---

page_filter = vm.Page(
    title="Cascader vs Dropdown as Filter",
    components=[
        vm.Graph(
            id="graph-scatter",
            figure=px.scatter(gapminder_2007, x="lifeExp", y="gdpPercap", color="continent", hover_name="country"),
        ),
    ],
    controls=[
        vm.Filter(
            column_hierarchy=["continent", "country"],
            targets=["graph-scatter"],
            selector=vm.Cascader(title="Country (Cascader multi=True)", multi=True),
        ),
        vm.Filter(
            column_hierarchy=["continent", "country"],
            targets=["graph-scatter"],
            selector=vm.Cascader(title="Country (Cascader multi=False)", multi=False),
        ),
        vm.Filter(
            column="continent",
            targets=["graph-scatter"],
            selector=vm.Dropdown(title="Continent (Dropdown multi=True)", multi=True),
        ),
        vm.Filter(
            column="continent",
            targets=["graph-scatter"],
            selector=vm.Dropdown(title="Continent (Dropdown multi=False)", multi=False),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page_parameter, page_filter])

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True, port=8052)
