"""Example to show dashboard configuration."""

import pandas as pd

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data, filter_interaction
from vizro.tables import dash_data_table


def retrieve_avg_continent_data():
    """This is function returns gapminder data grouped by continent."""
    df = px.data.gapminder()
    mean = (
        df.groupby(by=["continent", "year"]).agg({"lifeExp": "mean", "pop": "mean", "gdpPercap": "mean"}).reset_index()
    )
    return mean


def create_variable_analysis():
    """Function returns a page with gapminder data to do variable analysis."""
    df_gapminder = px.data.gapminder()
    df_avg_gapminder = retrieve_avg_continent_data()

    page_variable = vm.Page(
        title="Variable Analysis",
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
            row_gap="25px",
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
                figure=px.choropleth(
                    df_gapminder,
                    locations="iso_alpha",
                    color="lifeExp",
                    hover_name="country",
                    animation_frame="year",
                    labels={
                        "year": "year",
                        "lifeExp": "Life expectancy",
                        "pop": "Population",
                        "gdpPercap": "GDP per capita",
                    },
                    title="Global development over time",
                ),
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
                figure=px.box(
                    df_gapminder,
                    x="continent",
                    y="lifeExp",
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
                ),
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
                    df_avg_gapminder,
                    y="lifeExp",
                    x="year",
                    color="continent",
                    title="Development between 1952 and 2007",
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
                figure=px.bar(
                    df_avg_gapminder.query("year == 2007"),
                    x="lifeExp",
                    y="continent",
                    orientation="h",
                    title="Comparison of average metric for 2007",
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
                ),
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
    df_gapminder = px.data.gapminder()

    page_relation_analysis = vm.Page(
        title="Relationship Analysis",
        layout=vm.Layout(
            grid=[[0, 0, 0, 0, 1]] + [[2, 2, 3, 3, 3]] * 4 + [[4, 4, 4, 4, 4]] * 5,
            row_min_height="100px",
            row_gap="24px",
        ),
        components=[
            vm.Card(
                text="""
                    Population, GDP per capita, and life expectancy are interconnected metrics that provide insights
                    into the socio-economic well-being of a country.
                    Rapid population growth can strain resources and infrastructure, impacting GDP per capita. Higher
                    GDP per capita often enables better healthcare and improved life expectancy, but other factors such
                    as healthcare quality and social policies also play significant roles.
            """
            ),
            vm.Card(
                text="""
                        #### Last updated
                        November, 2023
                    """
            ),
            vm.Graph(
                id="bar_relation_2007",
                figure=px.box(
                    df_gapminder.query("year == 2007"),
                    x="continent",
                    y="lifeExp",
                    color="continent",
                    hover_name="continent",
                    title="Relationship in 2007",
                    labels={
                        "gdpPercap": "GDP per capita",
                        "pop": "Population",
                        "lifeExp": "Life expectancy",
                        "continent": "Continent",
                    },
                    color_discrete_map={
                        "Africa": "#00b4ff",
                        "Americas": "#ff9222",
                        "Asia": "#3949ab",
                        "Europe": "#ff5267",
                        "Oceania": "#08bdba",
                    },
                    custom_data=["continent"],
                ),
                actions=[vm.Action(function=filter_interaction(targets=["scatter_relation_2007"]))],
            ),
            vm.Graph(
                id="scatter_relation_2007",
                figure=px.scatter(
                    df_gapminder.query("year == 2007"),
                    x="gdpPercap",
                    y="lifeExp",
                    size="pop",
                    color="continent",
                    hover_name="country",
                    size_max=60,
                    labels={
                        "gdpPercap": "GDP per capita",
                        "pop": "Population",
                        "lifeExp": "Life expectancy",
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
            vm.Graph(
                id="scatter_relation",
                figure=px.scatter(
                    df_gapminder,
                    x="gdpPercap",
                    y="lifeExp",
                    animation_frame="year",
                    animation_group="country",
                    size="pop",
                    color="continent",
                    hover_name="country",
                    facet_col="continent",
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
                ),
            ),
        ],
        controls=[
            vm.Parameter(
                targets=["scatter_relation_2007.x", "scatter_relation.x"],
                selector=vm.Dropdown(
                    options=["lifeExp", "gdpPercap", "pop"], multi=False, value="gdpPercap", title="Choose x-axis"
                ),
            ),
            vm.Parameter(
                targets=["scatter_relation_2007.y", "scatter_relation.y", "bar_relation_2007.y"],
                selector=vm.Dropdown(
                    options=["lifeExp", "gdpPercap", "pop"], multi=False, value="lifeExp", title="Choose y-axis"
                ),
            ),
            vm.Parameter(
                targets=["scatter_relation_2007.size", "scatter_relation.size"],
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
        layout=vm.Layout(grid=[[i] for i in range(5)], row_min_height="190px", row_gap="25px"),
        components=[
            vm.Card(
                text="""
                    ### Africa
                    ![](assets/images/continents/africa.svg#my-image)

                    Africa, a diverse and expansive continent, faces both challenges and progress in its socio-economic
                    landscape. In 2007, Africa's GDP per capita was approximately $3,000, reflecting relatively slower
                    growth compared to other continents like Oceania and Europe.

                    However, Africa has shown notable improvements in life expectancy over time, reaching 55 years in
                    2007. Despite these economic disparities, Africa's population has been steadily increasing,
                    reflecting its significant potential for development.
                """,
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
                """,
            ),
            vm.Card(
                text="""
                    ### Asia
                    ![](assets/images/continents/asia.svg#my-image)

                    Asia holds a central role in the global economy. It's growth in GDP per capita to $12,000 in 2007
                    and population has been significant, outpacing many other continents. In 2007, it boasted the
                    highest population among all continents, with countries like China and India leading the way.

                    Despite facing various socio-economic challenges, Asia's increasing life expectancy from 46 years
                    to 70 over the years reflects advancements in healthcare and overall well-being, making it a vital
                    region driving global progress and development.
                """,
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
                """,
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
                """,
            ),
        ],
    )
    return page_summary


def create_country_analysis():
    """Function returns a page to perform analysis on country level."""
    df_gapminder = px.data.gapminder()

    df_gapminder_agg = px.data.gapminder()
    df_gapminder_agg["lifeExp"] = df_gapminder_agg.groupby(by=["continent", "year"])["lifeExp"].transform("mean")
    df_gapminder_agg["gdpPercap"] = df_gapminder_agg.groupby(by=["continent", "year"])["gdpPercap"].transform("mean")
    df_gapminder_agg["pop"] = df_gapminder_agg.groupby(by=["continent", "year"])["pop"].transform("sum")

    df_gapminder["data"] = "Country"
    df_gapminder_agg["data"] = "Continent"

    df_gapminder = pd.concat([df_gapminder_agg, df_gapminder], ignore_index=True)

    page_country = vm.Page(
        title="Country Analysis",
        components=[
            vm.Table(
                id="table_country",
                title="Table Country",
                figure=dash_data_table(
                    id="dash_data_table_country",
                    data_frame=px.data.gapminder(),
                ),
                actions=[vm.Action(function=filter_interaction(targets=["line_country"]))],
            ),
            vm.Graph(
                id="line_country",
                figure=px.line(
                    df_gapminder,
                    title="Line Country",
                    x="year",
                    y="gdpPercap",
                    color="data",
                    labels={"year": "Year", "data": "Data", "gdpPercap": "GDP per capita"},
                    color_discrete_map={"Country": "#afe7f9", "Continent": "#003875"},
                    markers=True,
                    hover_name="country",
                ),
            ),
            vm.Button(
                text="Export data",
                actions=[
                    vm.Action(
                        function=export_data(
                            targets=["line_country"],
                        )
                    ),
                ],
            ),
        ],
        controls=[
            vm.Filter(column="continent", selector=vm.Dropdown(value="Europe", multi=False, title="Select continent")),
            vm.Filter(column="year", selector=vm.RangeSlider(title="Select timeframe", step=1, marks=None)),
        ],
    )
    return page_country


def create_home_page():
    """Function returns the homepage."""
    page_home = vm.Page(
        title="Homepage",
        layout=vm.Layout(grid=[[0, 1], [2, 3]], row_gap="16px", col_gap="24px"),
        components=[
            vm.Card(
                text="""
                    ![](assets/images/icons/content/hypotheses.svg#icon-top)

                    ### Variable Analysis

                    Analyzing population, GDP per capita and life expectancy on country and continent level.
                """,
                href="/variable-analysis",
            ),
            vm.Card(
                text="""
                        ![](assets/images/icons/content/hypotheses.svg#icon-top)

                        ### Relationship Analysis

                        Investigating the interconnection between population, GDP per capita and life expectancy.
                    """,
                href="/relationship-analysis",
            ),
            vm.Card(
                text="""
                    ![](assets/images/icons/content/collections.svg#icon-top)

                    ### Continent Summary

                    Summarizing the main findings for each continent.
                """,
                href="/continent-summary",
            ),
            vm.Card(
                text="""
                    ![](assets/images/icons/content/features.svg#icon-top)

                    ### Country Analysis

                    Discovering how the metrics differ for each country and export data for further investigation.
                """,
                href="/country-analysis",
            ),
        ],
    )
    return page_home


dashboard = vm.Dashboard(
    pages=[
        create_home_page(),
        create_variable_analysis(),
        create_relation_analysis(),
        create_continent_summary(),
        create_country_analysis(),
    ],
    navigation=vm.Navigation(
        pages={
            "Analysis": ["Homepage", "Variable Analysis", "Relationship Analysis", "Country Analysis"],
            "Summary": ["Continent Summary"],
        }
    ),
)

if __name__ == "__main__":
    Vizro(assets_folder="../assets").build(dashboard).run()
