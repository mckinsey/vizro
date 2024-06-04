# How to create advanced charts
Now, let's explore more advanced visualizations and use Vizro-AI for enhanced formatting.

We'll create an animated bar chart illustrating the population development of each continent over time. Run the code below and look at the result.

!!! example "Vizro-AI animated chart"

    === "Code for the cell"
        ```py
        from vizro_ai import VizroAI
        import vizro.plotly.express as px

        df = px.data.gapminder()

        vizro_ai = VizroAI()
        vizro_ai.plot(df, "The chart should be an animated stacked bar chart with population on the y axis and continent on the x axis with all respective countries, allowing you to observe changes in the population over consecutive years.")
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
        vizro_ai.plot(df, "The chart should be an animated stacked bar chart with population on the y axis and continent on the x axis with all respective countries, allowing you to observe changes in the population over consecutive years. Please improve layout.")
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
        vizro_ai.plot(df, "The chart should be an animated stacked bar chart with population on the y axis and continent on the x axis with all respective countries, allowing you to observe changes in the population over consecutive years. Make sure that y axis range fits entire data. Please improve layout and optimize layout of legend.")
        ```
    === "Result"
        [![AnimatedChart3]][AnimatedChart3]

    [AnimatedChart3]: ../../assets/tutorials/chart/animated_bar_chart_3.png

Congratulations! You've now gained insights into harnessing the power of a LLM and Vizro-AI for crafting advanced charts and improving formatting. Don't forget, enabling `explain=True` is a good way of learning more about how a chart can be further improved and formatted.

Advanced charts are well-suited for [Vizro](https://github.com/mckinsey/vizro/tree/main/vizro-core) dashboard applications. You can create a chart using `vizro-ai` to plug into your `vizro` dashboard in seconds!

![chart-into-dashboard](../../assets/tutorials/chart_into_dashboard.gif)
