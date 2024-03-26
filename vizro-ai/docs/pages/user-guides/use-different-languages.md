# How to create visualizations using different languages
Vizro-AI is versatile, supporting prompts and chart visualizations in languages other than English. Let's explore this capability with two examples, starting with Chinese where we inquire about visualizing the GDP per capita over time.

!!! example "Vizro-AI Chinese"

    === "Code for the cell"
        ```py
        from vizro_ai import VizroAI
        import vizro.plotly.express as px

        df = px.data.gapminder()

        vizro_ai = VizroAI()
        vizro_ai.plot(df, "请画一个世界年均GDP的趋势图")
        ```
    === "Result"
        [![ChineseChart]][ChineseChart]

    [ChineseChart]: ../../assets/tutorials/chart/ChineseExample.png

Subsequently, we'll switch to German and prompt the visualization of life expectancy in the United States over time, comparing it to the global life expectancy trend. For this example, we'll include `explain=True` to obtain comprehensive insights into both the data and the generated code.

!!! example "Vizro-AI German"

    === "Code for the cell"
        ```py
        from vizro_ai import VizroAI
        import vizro.plotly.express as px

        df = px.data.gapminder()

        vizro_ai = VizroAI()
        vizro_ai.plot(df, "Visualiere den Trend von der Lebenserwartung in USA über die Jahre im Vergleich zur Veränderung der weltweiten Lebenserwartung über die Jahre und kreiere eine deutsche Visualisierung", explain=True)
        ```
    === "Result"
        [![GermanChart]][GermanChart]

    [GermanChart]: ../../assets/tutorials/chart/GermanExample.png
