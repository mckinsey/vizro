# Advanced charts
This page explains how to use Vizro-AI to create charts with advanced visualizations and enhanced formatting.

## Animated map chart

We'll create an animated map chart illustrating the GDP per capita of each continent over time. Run the code below and look at the result.

!!! example "Vizro-AI animated chart"

    === "Code"
        ```py
        from vizro_ai import VizroAI
        import vizro.plotly.express as px

        df = px.data.gapminder()

        vizro_ai = VizroAI()
        fig = vizro_ai.plot(df, "Visualize GDP per capita over the years for each country using map chart.")
        fig.show()
        ```
    === "Result"
        [![AnimatedChart1]][AnimatedChart1]

    [AnimatedChart1]: ../../assets/tutorials/chart/advanced_chart_1.png

Having unveiled our animated map chart showcasing GDP per capita development per country, it's clear that the map area is small, and it is difficult to differentiate countries.
Next, we will try to tweak our prompt to improve the overall layout.

!!! example "Vizro-AI animated chart"

    === "Code"
        ```py
        from vizro_ai import VizroAI
        import vizro.plotly.express as px

        df = px.data.gapminder()

        vizro_ai = VizroAI()
        fig = vizro_ai.plot(df,
              """Visualize GDP per capita over the years for each country using animated map chart.
              Show countries on the map. Increase the width and height of the figure.""")
        fig.show()
        ```
    === "Result"
        [![AnimatedChart2]][AnimatedChart2]

    [AnimatedChart2]: ../../assets/tutorials/chart/advanced_chart_2.png


By incorporating the directive `Increase the width and height of the figure.` and `Show countries on the map.` we've successfully refined our animation.

Upon closer inspection, the title is too long and the color palette used does not match our needs. We can fix those issues with better and more specific prompting. Let's run the code below to visually improve the chart.

!!! example "Vizro-AI animated chart"

    === "Code"
        ```py
        from vizro_ai import VizroAI
        import vizro.plotly.express as px

        df = px.data.gapminder()

        vizro_ai = VizroAI()
        fig = vizro_ai.plot(df,
              """Visualize GDP per capita over the years for each country using animated map chart.
              Show countries on the map. Increase the width and height of the figure.
              Set title to be: `GDP per Capita over the years`. Use `Blues` as color sequence. """)
        fig.show()
        ```
    === "Result"
        [![AnimatedChart3]][AnimatedChart3]

    [AnimatedChart3]: ../../assets/tutorials/chart/animated_advanced_chart.gif

Congratulations! You've now gained insights into harnessing the power of a LLM and Vizro-AI for crafting advanced charts and improving formatting. Don't forget, enabling `return_elements=True` in `.plot()` and check `chart_insights` and `code_explanation` is a good way of learning more about how a chart can be further improved and formatted.


Advanced charts are well-suited for [Vizro](https://github.com/mckinsey/vizro/tree/main/vizro-core) dashboard applications. You can create a chart using `vizro-ai` to plug into your `vizro` dashboard in seconds!


## Polar bar chart

A polar bar chart is a circular graph where each axis represents a different variable, typically used for displaying cyclical or directional data.
It's suitable for comparing multiple variables across different categories or directions. Let's make one using Vizro-AI.


!!! example "Polar Bar Chart"

    === "Resulting chart"
        [![VizroAIChart1]][VizroAIChart1]

    === "Code for the cell"
        ```py
        import vizro_ai
        from vizro_ai import VizroAI
        import plotly.express as px

        from dotenv import load_dotenv
        load_dotenv()

        df = px.data.wind()

        vizro_ai = VizroAI(model="gpt-4o")
        fig = vizro_ai.plot(df,
                      """Describe wind frequency and direction using bar_polar chart.
                         Increase the width and height of the figure.
                         Improve layout by placing title to the left. Show legend""")
        fig.show()
        ```

    [VizroAIChart1]: ../../assets/user_guides/polar_bar_chart.png



## 3D surface plot

Let's explore how to generate a 3-dimensional surface plot with VizroAI.

!!! example "Surface plot"

    === "Resulting chart"
        [![VizroAIChart3]][VizroAIChart3]

    === "Code for the cell"
        ```py
        import vizro_ai
        from vizro_ai import VizroAI
        import plotly.express as px

        from dotenv import load_dotenv
        load_dotenv()

        df = px.data.gapminder()

        vizro_ai = VizroAI(model="gpt-4o")
        fig = vizro_ai.plot(df, "create a surface plot")
        fig.show()
        ```

    [VizroAIChart3]: ../../assets/user_guides/surface_plot.gif
