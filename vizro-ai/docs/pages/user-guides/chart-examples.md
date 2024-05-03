# Explore VizroAI

In this tutorial, we walk through the process of creating some of the more complex plotly charts. The examples use data from the [plotly express data package](https://plotly.com/python-api-reference/generated/plotly.express.data.html).

## Create Polar Bar Chart with VizroAI

Polar Bar Charts are mostly used to visualize wind speed and direction at a given location, and with VizroAI you can create one with few lines of code.
In the example below we will use OpenAI `"gpt-4-0613"` model as we are going to request some specific updates to the layout of the chart.

!!! example "Polar Bar Chart"

    === "Code for the cell"
        ```py
        import vizro_ai
        from vizro_ai import VizroAI
        import plotly.express as px

        from dotenv import load_dotenv
        load_dotenv()

        df = px.data.wind()

        vizro_ai = VizroAI(model="gpt-4-0613")
        vizro_ai.plot(df,
                      """Describe wind frequency and direction using bar_polar chart.
                         Increase the width and height of the figure.
                         Improve layout by placing title to the left. Show legend""", explain=True)

        ```
    === "Resulting chart"
        [![VizroAIChart]][VizroAIChart]

    [VizroAIChart]: ../../assets/user_guides/polar_bar_chart.png

    === "Resulting insights"
        [![VizroAIChartIns]][VizroAIChartIns]

    [VizroAIChartIns]: ../../assets/user_guides/polar_bar_chart_insights.png


## Maps chart with Vizro-AI

Next chart we are going to explore is a map chart. In this example as well we will use OpenAI `"gpt-4-0613"` model as we need to make certain alterations to the chart layout that will enable us to clearly present the date.
We will request certain font type to be used, as well as several improvements to the chart layout.

!!! example "Polar Bar Chart"

    === "Code for the cell"
        ```py
        import vizro_ai
        from vizro_ai import VizroAI
        import plotly.express as px

        from dotenv import load_dotenv
        load_dotenv()

        df = px.data.wind()

        vizro_ai = VizroAI(model="gpt-4-0613")
        vizro_ai.plot(df,
                      """Describe population size changes over the years using bubble map chart. Use population to color the bubbles.
                         Improve layout by using Arial font. Increase the width and height of the map area. Outline continents on the map.
                         Show countries on the map.
                         Increase the width and height of the figure.""", explain=True)

        ```
    === "Resulting chart"
        [![VizroAIChart]][VizroAIChart]

    [VizroAIChart]: ../../assets/user_guides/geo_map_chart.gif

    === "Resulting insights"
        [![VizroAIChartIns]][VizroAIChartIns]

    [VizroAIChartIns]: ../../assets/user_guides/geo_map_chart_insights.png
