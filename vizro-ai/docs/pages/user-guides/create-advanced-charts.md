# Advanced charts
This page explains how to use Vizro-AI to create charts with advanced visualizations and enhanced formatting.

## How to increase the number of retries 

When making complex requests to Vizro-AI, you may sometimes find that the `plot` function returns an error that it has exceeded the number of debug retries. One option is to rephrase the prompt text in your request, but you can also adjust the `max_debug_retry` parameter to increase the number of retries from the default value of 3. 

For example, if you would like adjust to 5 retries, you can set `max_debug_retry = 5` in the plot function:

```py
vizro_ai.plot(df = df, user_input = "your user input", max_debug_retry= 5)
```
## Animated bar chart

We'll create an animated bar chart illustrating the population development of each continent over time. Run the code below and look at the result.

!!! example "Vizro-AI animated chart"

    === "Code for the cell"
        ```py
        from vizro_ai import VizroAI
        import vizro.plotly.express as px

        df = px.data.gapminder()

        vizro_ai = VizroAI()
        fig = vizro_ai.plot(df, "The chart should be an animated stacked bar chart with population on the y axis and continent on the x axis with all respective countries, allowing you to observe changes in the population over consecutive years.")
        fig.show()
        ```
    === "Result"
        [![AnimatedChart1]][AnimatedChart1]

    [AnimatedChart1]: ../../assets/tutorials/chart/animated_bar_chart_1.png

Having unveiled our animated bar chart showcasing population development per country, it's clear that crucial details are overshadowed by the legend. Next, we will try to tweak our prompt to group the countries into continents and improve the overall layout.

!!! example "Vizro-AI animated chart"

    === "Code for the cell"
        ```py
        from vizro_ai import VizroAI
        import vizro.plotly.express as px

        df = px.data.gapminder()

        vizro_ai = VizroAI()
        fig = vizro_ai.plot(df, "The chart should be an animated stacked bar chart with population on the y axis and continent on the x axis with all respective countries, allowing you to observe changes in the population over consecutive years. Please improve layout.")
        fig.show()
        ```
    === "Result"
        [![AnimatedChart2]][AnimatedChart2]

    [AnimatedChart2]: ../../assets/tutorials/chart/animated_bar_chart_2.png


By incorporating the directive `Please improve layout`, we've successfully refined our animation and are now able to better interpret our result.

Upon closer inspection, two challenges emerge: the legend overlaps the x-axis and the y-axis range is insufficient to capture the full spectrum of Asia's population development. Let's run the code below to improve the chart.

!!! example "Vizro-AI animated chart"

    === "Code for the cell"
        ```py
        from vizro_ai import VizroAI
        import vizro.plotly.express as px

        df = px.data.gapminder()

        vizro_ai = VizroAI()
        fig = vizro_ai.plot(df, "The chart should be an animated stacked bar chart with population on the y axis and continent on the x axis with all respective countries, allowing you to observe changes in the population over consecutive years. Make sure that y axis range fits entire data. Please improve layout and optimize layout of legend.")
        fig.show()
        ```
    === "Result"
        [![AnimatedChart3]][AnimatedChart3]

    [AnimatedChart3]: ../../assets/tutorials/chart/animated_bar_chart_3.png

Congratulations! You've now gained insights into harnessing the power of a LLM and Vizro-AI for crafting advanced charts and improving formatting. Don't forget, enabling `explain=True` is a good way of learning more about how a chart can be further improved and formatted.

Advanced charts are well-suited for [Vizro](https://github.com/mckinsey/vizro/tree/main/vizro-core) dashboard applications. You can create a chart using `vizro-ai` to plug into your `vizro` dashboard in seconds!

![chart-into-dashboard](../../assets/tutorials/chart_into_dashboard.gif)
