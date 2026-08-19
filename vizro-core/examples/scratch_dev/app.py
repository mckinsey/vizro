"""Showcase dashboard for Vizro's automatic consistent-color feature.

Every chart below is colored by "continent" or "country". None of them passes an explicit
`color_discrete_map`, yet a given continent/country always renders in the same color everywhere it
appears - across chart types, across pages, and as filters change what data a chart shows. That's the
new default behavior implemented in `vizro.models._components.graph._apply_consistent_colors`.
"""

import plotly.graph_objects as go

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture

# Colors assigned to categories are cached process-wide (see vizro.themes._consistent_colors), so a custom
# chart can look up the exact same color Vizro would assign automatically to a plotly.express chart.
from vizro.themes._consistent_colors import _consistent_color_discrete_map

df = px.data.gapminder()

# Countries that appear across several of the pages below (rankings differ by year/metric, but the
# overlapping names - e.g. United States, Japan - are exactly what should keep a stable color).
featured_countries = ["United States", "China", "India", "Japan", "Germany", "Brazil", "Norway"]


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


# --- Page 2: country rankings (Africa only), deliberately using different country subsets per chart --------
df_europe = df[df["continent"] == "Europe"]

top_population_2007 = df_europe[df_europe["year"] == 2007].nlargest(10, "lifeExp").sort_values("lifeExp")
bar_population = px.bar(
    top_population_2007,
    x="lifeExp",
    y="country",
    color="country",
    orientation="h",
    title="Top 10 Countries by life expectancy",
    labels={"pop": "Population", "country": "Country"},
)

top_gdp_2007 = df_europe[df_europe["year"] == 2007].nlargest(10, "gdpPercap").sort_values("gdpPercap")
bar_gdp = px.bar(
    top_gdp_2007,
    x="gdpPercap",
    y="country",
    color="country",
    orientation="h",
    title="Top 10 Countries by GDP per Capita (2007)",
    labels={"gdpPercap": "GDP per capita", "country": "Country"},
)

featured_countries_1 = ["Italy", "France", "Ireland", "Greece", "Iceland", "Norway", "Portugal"]
line_trend = px.line(
    df_europe[df_europe["country"].isin(featured_countries_1)],
    x="year",
    y="lifeExp",
    color="country",
    markers=True,
    title="Life Expectancy Trend for Major Economies",
    labels={"lifeExp": "Life expectancy", "year": "Year", "country": "Country"},
)

page_rankings = vm.Page(
    title="Country Rankings",
    description="These three charts each rank a different, non-overlapping-by-design set of African "
    "countries (top population in 2007, top GDP per capita in 2007, a fixed watchlist across all years). "
    "Countries that show up more than once - e.g. Norway, Iceland - keep the exact same color everywhere.",
    components=[
        vm.Graph(figure=bar_population),
        vm.Graph(figure=bar_gdp),
        vm.Graph(figure=line_trend),
    ],
    layout=vm.Grid(grid=[[0, 1], [2, 2]]),
)


# --- Page 3: filtering a chart changes which countries it shows, colors still don't move -------------------
df_2007 = df[df["year"] == 2007]

scatter_filtered = px.scatter(
    df_2007,
    x="gdpPercap",
    y="lifeExp",
    size="pop",
    color="country",
    hover_name="country",
    log_x=True,
    size_max=40,
    title="GDP vs. Life Expectancy (2007)",
    labels={"gdpPercap": "GDP per capita", "lifeExp": "Life expectancy"},
)

bar_filtered = px.bar(
    df_2007.sort_values("lifeExp"),
    x="lifeExp",
    y="country",
    color="country",
    orientation="h",
    title="Life Expectancy Ranking (2007)",
    labels={"lifeExp": "Life expectancy", "country": "Country"},
)


# --- Page 4: a custom chart, manually reusing Vizro's internal color registry -------------------------------
@capture("graph")
def life_expectancy_slopechart(data_frame, start_year, end_year, category_column="country"):
    """Custom slopechart comparing a metric between two years, one line per category.

    Custom `@capture("graph")` charts aren't covered by Vizro's automatic color-syncing (that only applies
    to genuine plotly.express charts), so this reaches into `vizro.themes._consistent_colors` - the same
    registry Vizro itself uses - to color each country exactly as it's colored everywhere else in this
    dashboard.
    """
    categories = data_frame[category_column].unique()

    fig = go.Figure()
    for category in categories:
        category_data = data_frame[data_frame[category_column] == category]
        start = category_data.loc[category_data["year"] == start_year, "lifeExp"]
        end = category_data.loc[category_data["year"] == end_year, "lifeExp"]
        if start.empty or end.empty:
            continue

        fig.add_trace(
            go.Scatter(
                x=[str(start_year), str(end_year)],
                y=[start.iloc[0], end.iloc[0]],
                mode="lines+markers+text",
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
    description="A hand-built go.Figure slopechart for the same 'major economies' watchlist from Country "
    "Rankings, colored to match by reusing Vizro's color registry directly.",
    components=[
        vm.Graph(
            figure=life_expectancy_slopechart(
                df[df["country"].isin(featured_countries)],
                start_year=1952,
                end_year=2007,
            )
        ),
    ],
)


dashboard = vm.Dashboard(
    title="Gapminder: Consistent Colors Showcase",
    pages=[page_continents, page_rankings, page_custom],
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
