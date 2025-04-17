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

        [![AnimatedChart1]][animatedchart1]

Having unveiled our animated map chart showcasing GDP per capita development per country, it's clear that the map area is small, and it is difficult to differentiate countries. Next, we will try to tweak our prompt to improve the overall layout.

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

        [![AnimatedChart2]][animatedchart2]

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

        [![AnimatedChart3]][animatedchart3]

Congratulations! You've now gained insights into harnessing the power of a LLM and Vizro-AI for crafting advanced charts and improving formatting. Don't forget, enabling `return_elements=True` in `.plot()` and check `chart_insights` and `code_explanation` is a good way of learning more about how a chart can be further improved and formatted.

Advanced charts are well-suited for [Vizro](https://github.com/mckinsey/vizro/tree/main/vizro-core) dashboard applications. You can create a chart using `vizro-ai` to plug into your `vizro` dashboard in seconds!

[animatedchart1]: ../../assets/tutorials/chart/advanced_chart_1.png
[animatedchart2]: ../../assets/tutorials/chart/advanced_chart_2.png
[animatedchart3]: ../../assets/tutorials/chart/animated_advanced_chart.gif
