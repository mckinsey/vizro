# Generate visualizations using different languages

Vizro-AI is versatile, supporting prompts and chart visualizations in languages other than English. In this guide you will explore this capability with two examples, starting with Chinese where we inquire about visualizing the GDP per capita over time.

!!! example "Vizro-AI Chinese"

    === "Code for the cell"

        ```py
        from vizro_ai import VizroAI
        import vizro.plotly.express as px

        df = px.data.gapminder()

        vizro_ai = VizroAI()
        fig = vizro_ai.plot(df, "请画一个世界年均GDP的趋势图")
        fig.show()
        ```

    === "Result"

        [![ChineseChart]][chinesechart]

Subsequently, we'll switch to German and prompt the visualization of life expectancy in the United States over time, comparing it to the global life expectancy trend. For this example, we'll include `return_elements=True` to obtain comprehensive insights into both the data and the generated code.

!!! example "Vizro-AI German"

    === "Code for the cell"

        ```py
        from vizro_ai import VizroAI
        import vizro.plotly.express as px

        df = px.data.gapminder()

        vizro_ai = VizroAI()
        result = vizro_ai.plot(df, "Visualiere den Trend von der Lebenserwartung in USA über die Jahre im Vergleich zur Veränderung der weltweiten Lebenserwartung über die Jahre und kreiere eine deutsche Visualisierung", return_elements=True)
        print(f"Insight:\n{result.chart_insights}\n" )
        print(f"Code:\n{result.code_explanation}\n{result.code_vizro}\n" )
        result.get_fig_object(df).show()
        ```

    === "Result"

        [![GermanChart]][germanchart]

[chinesechart]: ../../assets/tutorials/chart/ChineseExample.png
[germanchart]: ../../assets/tutorials/chart/GermanExample.png
