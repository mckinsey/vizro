"""Example to show dashboard configuration."""

from typing import Optional

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data, filter_interaction
from vizro.models.types import capture
from vizro.tables import dash_ag_grid

gapminder = px.data.gapminder()
gapminder_mean = (
    gapminder.groupby(by=["continent", "year"])
    .agg({"lifeExp": "mean", "pop": "mean", "gdpPercap": "mean"})
    .reset_index()
)
gapminder_mean_2007 = gapminder_mean.query("year == 2007")

gapminder_transformed = gapminder.copy()
gapminder_transformed["lifeExp"] = gapminder.groupby(by=["continent", "year"])["lifeExp"].transform("mean")
gapminder_transformed["gdpPercap"] = gapminder.groupby(by=["continent", "year"])["gdpPercap"].transform("mean")
gapminder_transformed["pop"] = gapminder.groupby(by=["continent", "year"])["pop"].transform("sum")
gapminder_concat = pd.concat(
    [gapminder_transformed.assign(color="Continent Avg."), gapminder.assign(color="Country")], ignore_index=True
)


@capture("graph")
def variable_map(data_frame: pd.DataFrame = None, color: Optional[str] = None):
    """Custom choropleth figure that needs post update calls."""
    fig = px.choropleth(
        data_frame,
        locations="iso_alpha",
        color=color,
        hover_name="country",
        animation_frame="year",
        labels={
            "year": "year",
            "lifeExp": "Life expectancy",
            "pop": "Population",
            "gdpPercap": "GDP per capita",
        },
        title="Global development over time",
    )
    fig.update_layout(showlegend=False)
    fig.update_yaxes(automargin=True)
    fig.update_xaxes(automargin=True)
    fig.update_coloraxes(colorbar={"thickness": 10, "title": {"side": "right"}})
    return fig


@capture("graph")
def variable_boxplot(y: str, data_frame: pd.DataFrame = None):
    """Custom boxplot figure that needs post update calls."""
    fig = px.box(
        data_frame,
        x="continent",
        y=y,
        color="continent",
        labels={
            "year": "year",
            "lifeExp": "Life expectancy",
            "pop": "Population",
            "gdpPercap": "GDP per capita",
            "continent": "Continent",
        },
        title="Distribution per continent",
        color_discrete_map={
            "Africa": "#00b4ff",
            "Americas": "#ff9222",
            "Asia": "#3949ab",
            "Europe": "#ff5267",
            "Oceania": "#08bdba",
        },
    )
    fig.update_layout(showlegend=False)
    fig.update_yaxes(automargin=True)
    fig.update_xaxes(automargin=True)
    return fig


@capture("graph")
def variable_bar(x: str, data_frame: pd.DataFrame = None):
    """Custom bar figure that needs post update calls."""
    fig = px.bar(
        data_frame,
        x=x,
        y="continent",
        orientation="h",
        title="Continent comparison (2007)",
        labels={
            "year": "year",
            "continent": "Continent",
            "lifeExp": "Life expectancy",
            "pop": "Population",
            "gdpPercap": "GDP per capita",
        },
        color="continent",
        color_discrete_map={
            "Africa": "#00b4ff",
            "Americas": "#ff9222",
            "Asia": "#3949ab",
            "Europe": "#ff5267",
            "Oceania": "#08bdba",
        },
    )

    fig.update_layout(showlegend=False)
    fig.update_yaxes(automargin=True)
    fig.update_xaxes(automargin=True)
    return fig


@capture("graph")
def scatter_relation(x: str, y: str, size: str, data_frame: pd.DataFrame = None):
    """Custom scatter figure that needs post update calls."""
    fig = px.scatter(
        data_frame,
        x=x,
        y=y,
        animation_frame="year",
        animation_group="country",
        size=size,
        size_max=60,
        color="continent",
        hover_name="country",
        labels={
            "gdpPercap": "GDP per capita",
            "pop": "Population",
            "lifeExp": "Life expectancy",
            "continent": "Continent",
        },
        range_y=[25, 90],
        color_discrete_map={
            "Africa": "#00b4ff",
            "Americas": "#ff9222",
            "Asia": "#3949ab",
            "Europe": "#ff5267",
            "Oceania": "#08bdba",
        },
    )

    fig.update_layout(
        title="Relationship over time",
        legend={"orientation": "v", "yanchor": "bottom", "y": 0, "xanchor": "right", "x": 1},
    )
    fig.update_yaxes(automargin=True)
    fig.update_xaxes(automargin=True)
    return fig


def create_variable_analysis():
    """Function returns a page with gapminder data to do variable analysis."""
    page_variable = vm.Page(
        title="Variable Analysis",
        description="Analyzing population, GDP per capita and life expectancy on country and continent level",
        layout=vm.Layout(
            grid=[
                # fmt: off
                [0, 1, 1, 1],
                [2, 3, 3, 3],
                [4, 5, 5, 5],
                [6, 7, 7, 7],
                # fmt: on
            ],
            row_min_height="400px",
            row_gap="24px",
        ),
        components=[
            vm.Card(
                text="""
                    ### Overview
                    The world map provides initial insights into the variations of metrics across countries and
                    continents. Click on Play to see the animation and explore the development over time.

                    #### Observation
                    A global trend of increasing life expectancy emerges, with some exceptions in specific African
                    countries. Additionally, despite similar population growth rates across continents, the overall
                    global population continues to expand, with India and China leading the way.  Meanwhile, GDP per
                    capita experiences growth in most regions.

                """
            ),
            vm.Graph(
                id="variable_map",
                figure=variable_map(data_frame=gapminder, color="lifeExp"),
            ),
            vm.Card(
                text="""
                    ### Distribution
                    The boxplot illustrates the distribution of each metric across continents, facilitating comparisons
                    of life expectancy, GDP per capita, and population statistics.

                    Observations reveal that Europe and Oceania have the highest life expectancy and GDP per capita,
                    likely influenced by their smaller population growth. Additionally, Asia and America exhibit
                    notable GDP per capita outliers, indicating variations among countries within these continents or
                    large growth over the observed years.
                """
            ),
            vm.Graph(
                id="variable_boxplot",
                figure=variable_boxplot(data_frame=gapminder, y="lifeExp"),
            ),
            vm.Card(
                text="""
                    ### Development
                    The line chart tracks the variable's progress from 1952 to 2007, facilitating a deeper comprehension
                    of each metric.

                    #### Observation
                    Oceania and Europe are found to have the highest total GDP per capita and exhibit significant
                    growth. In contrast, Asia, Africa, and America demonstrate a more pronounced upward trend in
                    population increase compared to Europe and Oceania, suggesting that GDP per capita growth might be
                    influenced by relatively smaller population growth in the latter two continents.

                """
            ),
            vm.Graph(
                id="variable_line",
                figure=px.line(
                    gapminder_mean,
                    y="lifeExp",
                    x="year",
                    color="continent",
                    title="Avg. Development (1952 - 2007)",
                    labels={
                        "year": "Year",
                        "lifeExp": "Life expectancy",
                        "pop": "Population",
                        "gdpPercap": "GDP per capita",
                        "continent": "Continent",
                    },
                    color_discrete_map={
                        "Africa": "#00b4ff",
                        "Americas": "#ff9222",
                        "Asia": "#3949ab",
                        "Europe": "#ff5267",
                        "Oceania": "#08bdba",
                    },
                ),
            ),
            vm.Card(
                text="""
                    ### Recent status
                    Examining the data for 2007 provides insight into the current status of each continent and metrics.

                    #### Observation
                    Asia held the largest population, followed by America, Europe, Africa, and Oceania. Life expectancy
                    surpassed 70 years for all continents, except Africa with 55 years. GDP per capita aligns with
                    earlier findings, with Oceania and Europe reporting the highest values and Africa recording the
                    lowest.
                """
            ),
            vm.Graph(
                id="variable_bar",
                figure=variable_bar(data_frame=gapminder_mean_2007, x="lifeExp"),
            ),
        ],
        controls=[
            vm.Parameter(
                targets=["variable_map.color", "variable_boxplot.y", "variable_line.y", "variable_bar.x"],
                selector=vm.RadioItems(options=["lifeExp", "pop", "gdpPercap"], title="Select variable"),
            )
        ],
    )
    return page_variable


def create_relation_analysis():
    """Function returns a page to perform relation analysis."""
    page_relation_analysis = vm.Page(
        title="Relationship Analysis",
        description="Investigating the interconnection between population, GDP per capita and life expectancy",
        layout=vm.Layout(
            grid=[[0, 0, 0, 0, 0]] + [[1, 1, 1, 1, 1]] * 4,
            row_min_height="100px",
            row_gap="24px",
        ),
        components=[
            vm.Card(
                text="""
                    Population, GDP per capita, and life expectancy are interconnected metrics that provide insights
                    into the socioeconomic well-being of a country.
                    Rapid population growth can strain resources and infrastructure, impacting GDP per capita. Higher
                    GDP per capita often enables better healthcare and improved life expectancy, but other factors such
                    as healthcare quality and social policies also play significant roles.
            """
            ),
            vm.Graph(
                id="scatter_relation",
                figure=scatter_relation(data_frame=gapminder, x="gdpPercap", y="lifeExp", size="pop"),
            ),
        ],
        controls=[
            vm.Parameter(
                targets=["scatter_relation.x"],
                selector=vm.Dropdown(
                    options=["lifeExp", "gdpPercap", "pop"], multi=False, value="gdpPercap", title="Choose x-axis"
                ),
            ),
            vm.Parameter(
                targets=["scatter_relation.size"],
                selector=vm.Dropdown(
                    options=["lifeExp", "gdpPercap", "pop"], multi=False, value="pop", title="Choose bubble size"
                ),
            ),
        ],
    )
    return page_relation_analysis


def create_continent_summary():
    """Function returns a page with markdown including images."""
    page_summary = vm.Page(
        title="Continent Summary",
        description="Summarizing the main findings for each continent",
        layout=vm.Layout(grid=[[i] for i in range(5)], row_min_height="190px", row_gap="25px"),
        components=[
            vm.Card(
                text="""
                    ### Africa
                    ![](assets/images/continents/africa.svg#my-image)

                    Africa, a diverse and expansive continent, faces both challenges and progress in its socioeconomic
                    landscape. In 2007, Africa's GDP per capita was approximately $3,000, reflecting relatively slower
                    growth compared to other continents like Oceania and Europe.

                    However, Africa has shown notable improvements in life expectancy over time, reaching 55 years in
                    2007. Despite these economic disparities, Africa's population has been steadily increasing,
                    reflecting its significant potential for development.
                """
            ),
            vm.Card(
                text="""
                    ### Americas
                    ![](assets/images/continents/america.svg#my-image)

                    Comprising North and South America, Americas represents a region of vast geographical and cultural
                    diversity. In 2007, the continent experienced substantial population growth, with a diverse mix of
                    countries contributing to this expansion.

                    Although its GDP per capita of $11,000 in 2007 exhibited variations across countries, America
                    maintained similar levels to Asia, reflecting its economic significance. With North America
                    generally reporting higher life expectancy compared to South America, America remains a region of
                    opportunities and challenges.
                """
            ),
            vm.Card(
                text="""
                    ### Asia
                    ![](assets/images/continents/asia.svg#my-image)

                    Asia holds a central role in the global economy. It's growth in GDP per capita to $12,000 in 2007
                    and population has been significant, outpacing many other continents. In 2007, it boasted the
                    highest population among all continents, with countries like China and India leading the way.

                    Despite facing various socioeconomic challenges, Asia's increasing life expectancy from 46 years
                    to 70 over the years reflects advancements in healthcare and overall well-being, making it a vital
                    region driving global progress and development.
                """
            ),
            vm.Card(
                text="""
                    ### Europe
                    ![](assets/images/continents/europe.svg#my-image)

                    Europe boasts a strong and thriving economy. In 2007, it exhibited the second-highest GDP per
                    capita of $25,000 among continents, indicating sustained economic growth and development.

                    Europe's life expectancy surpassed 75 years, showcasing a high standard of living and
                    well-established healthcare systems. With its robust infrastructure, advanced industries, and
                    quality of life, Europe continues to be a leading force in the global economy. Between 1952 and
                    2007, Europe's population experienced moderate growth, with a factor of approximately 1.5,
                    notably lower compared to other continents like Asia and America.
                """
            ),
            vm.Card(
                text="""
                    ### Oceania
                    ![](assets/images/continents/oceania.svg#my-image)

                    Oceania, comprising countries like Australia and New Zealand, stands out with notable economic
                    prosperity and longer life expectancy. In 2007, it boasted the highest GDP per capita of $27,000
                    among continents and exhibited one of the highest life expectancy levels, surpassing 80 years.

                    Despite a relatively smaller population size, Oceania's strong economic growth has contributed
                    to improved living standards and overall well-being of its population.
                """
            ),
        ],
    )
    return page_summary


def create_benchmark_analysis():
    """Function returns a page to perform analysis on country level."""
    # Apply formatting to grid columns
    cellStyle = {
        "styleConditions": [
            {
                "condition": "params.value < 1045",
                "style": {"backgroundColor": "#ff9222"},
            },
            {
                "condition": "params.value >= 1045 && params.value <= 4095",
                "style": {"backgroundColor": "#de9e75"},
            },
            {
                "condition": "params.value > 4095 && params.value <= 12695",
                "style": {"backgroundColor": "#aaa9ba"},
            },
            {
                "condition": "params.value > 12695",
                "style": {"backgroundColor": "#00b4ff"},
            },
        ]
    }
    columnsDefs = [
        {"field": "country", "flex": 3},
        {"field": "continent", "flex": 3},
        {"field": "year", "flex": 2},
        {"field": "lifeExp", "cellDataType": "numeric", "flex": 3},
        {"field": "gdpPercap", "cellDataType": "dollar", "cellStyle": cellStyle, "flex": 3},
        {"field": "pop", "flex": 3},
    ]

    page_country = vm.Page(
        title="Benchmark Analysis",
        description="Discovering how the metrics differ for each country and export data for further investigation",
        layout=vm.Layout(grid=[[0, 1]] * 5 + [[2, -1]]),
        components=[
            vm.AgGrid(
                title="Click on a cell in country column:",
                figure=dash_ag_grid(data_frame=gapminder, columnDefs=columnsDefs, dashGridOptions={"pagination": True}),
                actions=[vm.Action(function=filter_interaction(targets=["line_country"]))],
            ),
            vm.Graph(
                id="line_country",
                figure=px.line(
                    gapminder_concat,
                    title="Country vs. Continent",
                    x="year",
                    y="gdpPercap",
                    color="color",
                    labels={"year": "Year", "data": "Data", "gdpPercap": "GDP per capita"},
                    color_discrete_map={"Country": "#afe7f9", "Continent": "#003875"},
                    markers=True,
                    hover_name="country",
                ),
            ),
            vm.Button(text="Export data", actions=[vm.Action(function=export_data(targets=["line_country"]))]),
        ],
        controls=[
            vm.Filter(column="continent", selector=vm.Dropdown(value="Europe", multi=False, title="Select continent")),
            vm.Filter(column="year", selector=vm.RangeSlider(title="Select timeframe", step=1, marks=None)),
            vm.Parameter(
                targets=["line_country.y"],
                selector=vm.Dropdown(
                    options=["lifeExp", "gdpPercap", "pop"], multi=False, value="gdpPercap", title="Choose y-axis"
                ),
            ),
        ],
    )
    return page_country


def create_home_page():
    """Function returns the homepage."""
    page_home = vm.Page(
        title="Homepage",
        description="Vizro demo app for studying gapminder data",
        layout=vm.Layout(grid=[[0, 1], [2, 3]]),
        components=[
            vm.Card(
                text="""
                    ![](assets/images/icons/hypotheses.svg#icon-top)

                    ### Variable Analysis

                    Analyzing population, GDP per capita and life expectancy on country and continent level.
                """,
                href="/variable-analysis",
            ),
            vm.Card(
                text="""
                        ![](assets/images/icons/hypotheses.svg#icon-top)

                        ### Relationship Analysis

                        Investigating the interconnection between population, GDP per capita and life expectancy.
                    """,
                href="/relationship-analysis",
            ),
            vm.Card(
                text="""
                    ![](assets/images/icons/collections.svg#icon-top)

                    ### Continent Summary

                    Summarizing the main findings for each continent.
                """,
                href="/continent-summary",
            ),
            vm.Card(
                text="""
                    ![](assets/images/icons/features.svg#icon-top)

                    ### Benchmark Analysis

                    Discovering how the metrics differ for each country compared to the continent average
                    and export data for further investigation.
                """,
                href="/benchmark-analysis",
            ),
        ],
    )
    return page_home


dashboard = vm.Dashboard(
    title="Vizro Demo",
    pages=[
        create_home_page(),
        create_variable_analysis(),
        create_relation_analysis(),
        create_continent_summary(),
        create_benchmark_analysis(),
    ],
    navigation=vm.Navigation(
        nav_selector=vm.NavBar(
            items=[
                vm.NavLink(label="Homepage", pages=["Homepage"], icon="Home"),
                vm.NavLink(
                    label="Analysis",
                    pages=["Variable Analysis", "Relationship Analysis", "Benchmark Analysis"],
                    icon="Stacked Bar Chart",
                ),
                vm.NavLink(label="Summary", pages=["Continent Summary"], icon="Globe"),
            ]
        )
    ),
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
