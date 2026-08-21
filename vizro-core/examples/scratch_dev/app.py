"""Showcase dashboard for Vizro's opt-in consistent-color feature (vm.Dashboard(consistent_colors=True)).

Every country-colored chart below draws from the same fixed pool of exactly 10 European countries
(EUROPEAN_COUNTRIES) - one per color in the qualitative palette, so nothing ever collides. None of them
passes an explicit `color_discrete_map`, yet a given country always renders in the same color everywhere it
appears - across chart types, across pages, and as a filter changes which countries a chart shows. This
only happens because the dashboard below opts in with `consistent_colors=True`; without it, each chart
would fall back to Plotly's normal per-figure color assignment (see
`vizro.models._components.graph._apply_consistent_colors`).

Page 4 additionally shows how to opt a custom `@capture("graph")` chart into the same colors, since that
automatic behavior only covers genuine plotly.express charts.

Note: with more distinct categories in a dashboard than colors in the qualitative palette (10), colors
will start to repeat - see the "Consistent categorical colors across charts" section of themes.md.
"""

import plotly.graph_objects as go

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import color_manager
from vizro.models.types import capture

df = px.data.gapminder()

# Exactly 10 countries - one per color in the qualitative palette - reused across every country-colored
# chart in this dashboard, so no two countries are ever forced to share a color (continents, on the other
# hand, are a different categorical column entirely and never appear in the same legend as a country).
EUROPEAN_COUNTRIES = [
    "France",
    "Germany",
    "Italy",
    "Netherlands",
    "Spain",
    "Sweden",
    "Belgium",
    "Norway",
    "Ireland",
    "Portugal",
]
df_europe = df[df["country"].isin(EUROPEAN_COUNTRIES)]


# --- Page 1: continents, several chart types and aggregations, one shared color per continent -------------
bubble_chart = px.scatter(
    df,
    x="gdpPercap",
    y="lifeExp",
    size="pop",
    color="continent",
    hover_name="country",
    log_x=True,
    size_max=60,
    animation_frame="year",
    animation_group="country",
    range_x=[100, 100_000],
    range_y=[20, 90],
    title="GDP per Capita vs. Life Expectancy Over Time",
    labels={"gdpPercap": "GDP per capita", "lifeExp": "Life expectancy", "pop": "Population"},
)

box_chart = px.box(
    df[df["year"] == 2007],
    x="continent",
    y="lifeExp",
    color="continent",
    points="all",
    title="Life Expectancy Spread by Continent (2007)",
    labels={"lifeExp": "Life expectancy", "continent": "Continent"},
)

population_by_continent = df.groupby(["year", "continent"], as_index=False)["pop"].sum()
area_chart = px.area(
    population_by_continent,
    x="year",
    y="pop",
    color="continent",
    title="Population Growth by Continent",
    labels={"pop": "Population", "year": "Year", "continent": "Continent"},
)

page_continents = vm.Page(
    title="Continents at a Glance",
    description="The same 5 continent colors are reused across an animated bubble chart, a box plot and a "
    "stacked area chart - three very different chart types and data shapes.",
    components=[
        vm.Graph(figure=bubble_chart),
        vm.Graph(figure=box_chart),
        vm.Graph(figure=area_chart),
    ],
    layout=vm.Grid(grid=[[0, 0], [1, 2]]),
)


# --- Page 2: country rankings, deliberately using different years/metrics/subsets per chart ----------------
top_lifeexp_2007 = df_europe[df_europe["year"] == 2007].nlargest(6, "lifeExp").sort_values("lifeExp")
bar_lifeexp = px.bar(
    top_lifeexp_2007,
    x="lifeExp",
    y="country",
    color="country",
    orientation="h",
    title="Top 6 Countries by Life Expectancy (2007)",
    labels={"lifeExp": "Life expectancy", "country": "Country"},
)

top_gdp_1992 = df_europe[df_europe["year"] == 1992].nlargest(6, "gdpPercap").sort_values("gdpPercap")
bar_gdp = px.bar(
    top_gdp_1992,
    x="gdpPercap",
    y="country",
    color="country",
    orientation="h",
    title="Top 6 Countries by GDP per Capita (1992)",
    labels={"gdpPercap": "GDP per capita", "country": "Country"},
)

line_trend = px.line(
    df_europe,
    x="year",
    y="lifeExp",
    color="country",
    markers=True,
    title="Life Expectancy Trend (1952-2007)",
    labels={"lifeExp": "Life expectancy", "year": "Year", "country": "Country"},
)

page_rankings = vm.Page(
    title="Country Rankings",
    description="Three different rankings of the same 10 European countries - different years, different "
    "metrics, different subsets of 6 - yet any country that shows up in more than one chart keeps exactly "
    "the same color throughout.",
    components=[
        vm.Graph(figure=bar_lifeexp),
        vm.Graph(figure=bar_gdp),
        vm.Graph(figure=line_trend),
    ],
    layout=vm.Grid(grid=[[0, 1], [2, 2]]),
)


# --- Page 3: filtering shrinks which countries a chart shows, but colors never move ------------------------
df_europe_2007 = df_europe[df_europe["year"] == 2007]

scatter_filtered = px.scatter(
    df_europe_2007,
    x="gdpPercap",
    y="lifeExp",
    size="pop",
    color="country",
    hover_name="country",
    size_max=50,
    title="GDP vs. Life Expectancy (2007)",
    labels={"gdpPercap": "GDP per capita", "lifeExp": "Life expectancy"},
)

bar_filtered = px.bar(
    df_europe_2007.sort_values("lifeExp"),
    x="lifeExp",
    y="country",
    color="country",
    orientation="h",
    title="Life Expectancy Ranking (2007)",
    labels={"lifeExp": "Life expectancy", "country": "Country"},
)

page_interactive = vm.Page(
    title="Interactive Explorer",
    description="Use the filter to remove countries from both charts below. Vizro re-renders them on every "
    "filter change, but any country that's still shown keeps the exact color it had before filtering - "
    "colors are re-resolved from the same dashboard-wide registry on every render, not baked in once.",
    components=[
        vm.Graph(figure=scatter_filtered),
        vm.Graph(figure=bar_filtered),
    ],
    controls=[vm.Filter(column="country")],
    layout=vm.Grid(grid=[[0, 1]]),
)


# --- Page 4: a custom chart, manually reusing Vizro's internal color registry -------------------------------
@capture("graph")
def life_expectancy_slopechart(data_frame, start_year, end_year, category_column="country"):
    """Custom slopechart comparing a metric between two years, one line per category.

    Custom `@capture("graph")` charts aren't covered by `vm.Dashboard(consistent_colors=True)` automatically
    - that only applies to genuine plotly.express charts - so this reaches into
    `vizro.managers.color_manager` (currently a private API) directly, to color each country exactly as
    it's colored everywhere else in this dashboard.
    """
    categories = data_frame[category_column].unique()
    color_map = color_manager._get_color_discrete_map(categories)

    fig = go.Figure()
    for category in categories:
        category_data = data_frame[data_frame[category_column] == category]
        start = category_data.loc[category_data["year"] == start_year, "lifeExp"]
        end = category_data.loc[category_data["year"] == end_year, "lifeExp"]
        if start.empty or end.empty:
            continue

        color = color_map[category]
        fig.add_trace(
            go.Scatter(
                x=[str(start_year), str(end_year)],
                y=[start.iloc[0], end.iloc[0]],
                mode="lines+markers+text",
                line={"color": color, "width": 3},
                marker={"color": color, "size": 10},
                text=[category, ""],
                textposition="middle left",
                name=category,
            )
        )

    fig.update_layout(
        yaxis_title="Life expectancy",
        xaxis={"type": "category"},
        showlegend=True,
    )
    return fig


page_custom = vm.Page(
    title="Custom Chart: Slopechart",
    description="A hand-built go.Figure slopechart for the same 10 European countries, colored to match "
    "the rest of the dashboard by reaching into Vizro's internal color registry directly.",
    components=[
        vm.Graph(
            figure=life_expectancy_slopechart(
                df_europe,
                start_year=1952,
                end_year=2007,
            )
        ),
    ],
)


dashboard = vm.Dashboard(
    title="Gapminder: Consistent Colors Showcase",
    pages=[page_continents, page_rankings, page_interactive, page_custom],
    consistent_colors=True,
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
