"""Example to show dashboard configuration specified as a dictionary."""

import pandas as pd

import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data, filter_interaction
from vizro.managers import data_manager
from vizro.models import Dashboard
from vizro.tables import dash_data_table


def retrieve_gapminder():
    """This is a function that returns gapminder data."""
    return px.data.gapminder()


def retrieve_gapminder_year(year: int):
    """This is a function that returns gapminder data for a year."""
    return px.data.gapminder().query(f"year == {year}")


def retrieve_gapminder_continent_comparison():
    """This is a function adds aggregated continent information to gapminder data."""
    df_gapminder = px.data.gapminder()
    df_gapminder_agg = px.data.gapminder()

    df_gapminder_agg["lifeExp"] = df_gapminder_agg.groupby(by=["continent", "year"])["lifeExp"].transform("mean")
    df_gapminder_agg["gdpPercap"] = df_gapminder_agg.groupby(by=["continent", "year"])["gdpPercap"].transform("mean")
    df_gapminder_agg["pop"] = df_gapminder_agg.groupby(by=["continent", "year"])["pop"].transform("sum")

    df_gapminder["data"] = "Country"
    df_gapminder_agg["data"] = "Continent"

    df_gapminder_comp = pd.concat([df_gapminder_agg, df_gapminder], ignore_index=True)

    return df_gapminder_comp


def retrieve_avg_gapminder():
    """This is a function that returns aggregated gapminder data."""
    df = px.data.gapminder()
    mean = (
        df.groupby(by=["continent", "year"]).agg({"lifeExp": "mean", "pop": "mean", "gdpPercap": "mean"}).reset_index()
    )
    return mean


def retrieve_avg_gapminder_year(year: int):
    """This is a function that returns aggregated gapminder data for a specific year."""
    return retrieve_avg_gapminder().query(f"year == {year}")


# If you're not interested in lazy loading then you could just do data_manager["gapminder"] = px.data.gapminder()
data_manager["gapminder"] = retrieve_gapminder
data_manager["gapminder_2007"] = lambda: retrieve_gapminder_year(2007)
data_manager["gapminder_avg"] = retrieve_avg_gapminder
data_manager["gapminder_avg_2007"] = lambda: retrieve_avg_gapminder_year(2007)
data_manager["gapminder_country_analysis"] = retrieve_gapminder_continent_comparison

page_variable = {
    "title": "Variable Analysis",
    "layout": {
        "grid": [
            # fmt: off
            [0, 1, 1, 1],
            [2, 3, 3, 3],
            [4, 5, 5, 5],
            [6, 7, 7, 7],
            # fmt: on,
        ],
        "row_min_height": "400px",
        "row_gap": "25px",
    },
    "components": [
        {
            "type": "card",
            "text": """
                ### Overview
                The world map provides initial insights into the variations of metrics across countries and
                continents. Click on Play to see the animation and explore the development over time.

                #### Observation
                A global trend of increasing life expectancy emerges, with some exceptions in specific African
                countries. Additionally, despite similar population growth rates across continents, the overall
                global population continues to expand, with India and China leading the way.  Meanwhile, GDP per
                capita experiences growth in most regions.
            """,
        },
        {
            "type": "graph",
            "id": "variable_map",
            "figure": px.choropleth(
                "gapminder",
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
        },
        {
            "type": "card",
            "text": """
                    ### Distribution
                    The boxplot illustrates the distribution of each metric across continents, facilitating comparisons
                    of life expectancy, GDP per capita, and population statistics.

                    #### Observation
                    Observations reveal that Europe and Oceania have the highest life expectancy and GDP per capita,
                    likely influenced by their smaller population growth. Additionally, Asia and America exhibit
                    notable GDP per capita outliers, indicating variations among countries within these continents or
                    large growth over the observed years.
            """,
        },
        {
            "type": "graph",
            "id": "variable_boxplot",
            "figure": px.box(
                "gapminder",
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
        },
        {
            "type": "card",
            "text": """
                    ### Development
                    The line chart tracks the variable's progress from 1952 to 2007, facilitating a deeper comprehension
                    of each metric.

                    #### Observation
                    Oceania and Europe are found to have the highest total GDP per capita and exhibit significant
                    growth. In contrast, Asia, Africa, and America demonstrate a more pronounced upward trend in
                    population increase compared to Europe and Oceania, suggesting that GDP per capita growth might be
                    influenced by relatively smaller population growth in the latter two continents.
            """,
        },
        {
            "type": "graph",
            "id": "variable_line",
            "figure": px.line(
                "gapminder_avg",
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
        },
        {
            "type": "card",
            "text": """
                    ### Recent status
                    Examining the data for 2007 provides insight into the current status of each continent and metrics.

                    #### Observation
                    Asia held the largest population, followed by America, Europe, Africa, and Oceania. Life expectancy
                    surpassed 70 years for all continents, except Africa with 55 years. GDP per capita aligns with
                    earlier findings, with Oceania and Europe reporting the highest values and Africa recording the
                    lowest.
                """,
        },
        {
            "type": "graph",
            "id": "variable_bar",
            "figure": px.bar(
                "gapminder_avg_2007",
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
        },
    ],
    "controls": [
        {
            "type": "parameter",
            "targets": ["variable_map.color", "variable_boxplot.y", "variable_line.y", "variable_bar.x"],
            "selector": {"type": "radio_items", "title": "Select variable", "options": ["lifeExp", "pop", "gdpPercap"]},
        },
    ],
}

page_relation = {
    "title": "Relationship Analysis",
    "layout": {
        "grid": [[0, 0, 0, 0, 1]] + [[2, 2, 3, 3, 3]] * 4 + [[4, 4, 4, 4, 4]] * 5,
        "row_min_height": "100px",
        "row_gap": "24px",
    },
    "components": [
        {
            "type": "card",
            "text": """
                    Population, GDP per capita, and life expectancy are interconnected metrics that provide insights
                    into the socio-economic well-being of a country.
                    Rapid population growth can strain resources and infrastructure, impacting GDP per capita. Higher
                    GDP per capita often enables better healthcare and improved life expectancy, but other factors such
                    as healthcare quality and social policies also play significant roles.
            """,
        },
        {
            "type": "card",
            "text": """
                    #### Last updated
                    November, 2023
             """,
        },
        {
            "type": "graph",
            "id": "bar_relation_2007",
            "figure": px.box(
                "gapminder_2007",
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
            "actions": [
                {"function": filter_interaction(targets=["scatter_relation_2007"])},
            ],
        },
        {
            "type": "graph",
            "id": "scatter_relation_2007",
            "figure": px.scatter(
                "gapminder_2007",
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
        },
        {
            "type": "graph",
            "id": "scatter_relation",
            "figure": px.scatter(
                "gapminder",
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
        },
    ],
    "controls": [
        {
            "type": "parameter",
            "targets": ["scatter_relation_2007.x", "scatter_relation.x"],
            "selector": {
                "type": "dropdown",
                "title": "Choose x-axis",
                "options": ["lifeExp", "gdpPercap", "pop"],
                "multi": False,
                "value": "gdpPercap",
            },
        },
        {
            "type": "parameter",
            "targets": ["scatter_relation_2007.y", "scatter_relation.y", "bar_relation_2007.y"],
            "selector": {
                "type": "dropdown",
                "title": "Choose y-axis",
                "options": ["lifeExp", "gdpPercap", "pop"],
                "multi": False,
                "value": "lifeExp",
            },
        },
        {
            "type": "parameter",
            "targets": ["scatter_relation_2007.size", "scatter_relation.size"],
            "selector": {
                "type": "dropdown",
                "title": "Choose bubble size",
                "options": ["lifeExp", "gdpPercap", "pop"],
                "multi": False,
                "value": "pop",
            },
        },
    ],
}

page_continent = {
    "title": "Continent Summary",
    "layout": {"grid": [[i] for i in range(5)], "row_min_height": "190px", "row_gap": "26px"},
    "components": [
        {
            "type": "card",
            "text": """
                    ### Africa
                    ![](assets/images/continents/africa.svg#my-image)

                    Africa, a diverse and expansive continent, faces both challenges and progress in its socio-economic
                    landscape. In 2007, Africa's GDP per capita was approximately $3,000, reflecting relatively slower
                    growth compared to other continents like Oceania and Europe.

                    However, Africa has shown notable improvements in life expectancy over time, reaching 55 years in
                    2007. Despite these economic disparities, Africa's population has been steadily increasing,
                    reflecting its significant potential for development.
            """,
        },
        {
            "type": "card",
            "text": """
                    ### America
                    ![](assets/images/continents/america.svg#my-image)

                    Comprising North and South America, America represents a region of vast geographical and cultural
                    diversity. In 2007, the continent experienced substantial population growth, with a diverse mix of
                    countries contributing to this expansion.

                    Although its GDP per capita of $11,000 in 2007 exhibited variations across countries, America
                    maintained similar levels to Asia, reflecting its economic significance. With North America
                    generally reporting higher life expectancy compared to South America, America remains a region of
                    opportunities and challenges.
            """,
        },
        {
            "type": "card",
            "text": """
                    ### Asia
                    ![](assets/images/continents/asia.svg#my-image)

                    Asia holds a central role in the global economy. It's growth in GDP per capita to $12,000 in 2007
                    and population has been significant, outpacing many other continents. In 2007, it boasted the
                    highest population among all continents, with countries like China and India leading the way.

                    Despite facing various socio-economic challenges, Asia's increasing life expectancy from 46 years
                    to 70 over the years reflects advancements in healthcare and overall well-being, making it a vital
                    region driving global progress and development.
            """,
        },
        {
            "type": "card",
            "text": """
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
        },
        {
            "type": "card",
            "text": """
                    ### Oceania
                    ![](assets/images/continents/oceania.svg#my-image)

                    Oceania, comprising countries like Australia and New Zealand, stands out with notable economic
                    prosperity and longer life expectancy. In 2007, it boasted the highest GDP per capita of $27,000
                    among continents and exhibited one of the highest life expectancy levels, surpassing 80 years.

                    Despite a relatively smaller population size, Oceania's strong economic growth has contributed
                    to improved living standards and overall well-being of its population.
            """,
        },
    ],
}

page_country = {
    "title": "Country Analysis",
    "components": [
        {
            "type": "table",
            "id": "table_country",
            "title": "Table Country",
            "figure": dash_data_table(
                id="dash_data_table_country",
                data_frame="gapminder",
            ),
            "actions": [
                {"function": filter_interaction(targets=["line_country"])},
            ],
        },
        {
            "type": "graph",
            "id": "line_country",
            "figure": px.line(
                "gapminder_country_analysis",
                title="Line Country",
                x="year",
                y="gdpPercap",
                color="data",
                labels={"year": "Year", "data": "Data", "gdpPercap": "GDP per capita"},
                color_discrete_map={"Country": "#afe7f9", "Continent": "#003875"},
                markers=True,
                hover_name="country",
            ),
        },
        {
            "type": "button",
            "id": "export_data_button",
            "text": "Export data",
            "actions": [
                {"function": export_data(targets=["line_country"])},
            ],
        },
    ],
    "controls": [
        {
            "type": "filter",
            "column": "continent",
            "selector": {"type": "dropdown", "title": "Select continent", "multi": False, "value": "Europe"},
        },
        {
            "type": "filter",
            "column": "year",
            "selector": {"type": "range_slider", "title": "Select timeframe"},
        },
    ],
}

page_home = {
    "title": "Homepage",
    "layout": {
        "grid": [[0, 1], [2, 3]],
        "col_gap": "24px",
        "row_gap": "16px",
    },
    "components": [
        {
            "type": "card",
            "text": """
                    ![](assets/images/icons/content/hypotheses.svg#icon-top)

                    ### Variable Analysis

                    Analyzing population, GDP per capita and life expectancy on country and continent level.
            """,
            "href": "/variable-analysis",
        },
        {
            "type": "card",
            "text": """
                    ![](assets/images/icons/content/hypotheses.svg#icon-top)

                    ### Relationship Analysis

                    Investigating the interconnection between population, GDP per capita and life expectancy.
            """,
            "href": "/relationship-analysis",
        },
        {
            "type": "card",
            "text": """
                    ![](assets/images/icons/content/collections.svg#icon-top)

                    ### Continent Summary

                    Summarizing the main findings for each continent.
            """,
            "href": "/continent-summary",
        },
        {
            "type": "card",
            "text": """
                    ![](assets/images/icons/content/features.svg#icon-top)

                    ### Country Analysis

                    Discovering how the metrics differ for each country and export data for further investigation.
            """,
            "href": "/country-analysis",
        },
    ],
}

dashboard = {
    "pages": [page_home, page_variable, page_relation, page_continent, page_country],
    "navigation": {
        "pages": {
            "Analysis": ["Homepage", "Variable Analysis", "Relationship Analysis", "Country Analysis"],
            "Summary": ["Continent Summary"],
        }
    },
}

dashboard = Dashboard(**dashboard)

if __name__ == "__main__":
    Vizro(assets_folder="../assets").build(dashboard).run()
