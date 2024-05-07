# Explore VizroAI

In this tutorial, we walk through the process of creating more complex plotly charts. The examples use data from the [plotly express data package](https://plotly.com/python-api-reference/generated/plotly.express.data.html).
In the examples below we will use OpenAI `"gpt-4-0613"` model as we are going to request specific updates to the layout of the charts.

## Create Polar Bar Chart with VizroAI

Polar Bar Charts are mostly used to visualize data that has both magnitude and direction, such as wind speed and direction at specific locations.
They are particularly effective for displaying cyclical or directional data as they provide intuitive way of visualizing patterns in data across different directions.


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
        [![VizroAIChart1]][VizroAIChart1]

    [VizroAIChart1]: ../../assets/user_guides/polar_bar_chart.png


## Maps chart with Vizro-AI

Next chart we are going to explore is a map chart. Geo map charts allow us to explore and visualize the spatial relationships and patterns in the data, and often provide immediate insights that are not apparent when using other chart types.

!!! example "Map chart"

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
        [![VizroAIChart2]][VizroAIChart2]

    [VizroAIChart2]: ../../assets/user_guides/geo_map_chart.gif



## Distribution chart

Next chart we are going to explore with Vizro-AI is histogram, one of the most used charts for graphical representation of distribution of data.

!!! example "Histogram"

    === "Code for the cell"
        ```py
        import vizro_ai
        from vizro_ai import VizroAI
        import plotly.express as px

        from dotenv import load_dotenv
        load_dotenv()

        df = px.data.tips()

        vizro_ai = VizroAI(model="gpt-4-0613")
        vizro_ai.plot(df,
                     """Describe the distribution of total bills and tips using histogram. Set total tip on y axis, and total bill on x axis.
                        Include marginal rug plot. Improve layout.""", explain=True)

        ```
    === "Resulting chart"
        [![VizroAIChart3]][VizroAIChart3]

    [VizroAIChart3]: ../../assets/user_guides/histogram_chart.png
