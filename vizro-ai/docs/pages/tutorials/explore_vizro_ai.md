# Explore Vizro-AI
This tutorial serves as an exploration of the extended applications offered by Vizro-AI beyond the initial [quickstart guide](../tutorials/quickstart.md).

By the end of this tutorial, you will have gained an understanding of different language options and leveraging Vizro-AI to enhance the formatting your visualizations.

## Let's get started!
### 1. Install Vizro-AI and get ready to run your code
Before proceeding, ensure the installation of the `vizro_ai` package by following the steps outlined in the [installation guide](../user_guides/install.md). Once installed, you can execute your code either by pasting it into a Jupyter notebook cell or running it from a Python script.


??? tip "Beginners/Code novices"
    For those new to Python or virtual environments, a user-friendly alternative is available in the [installation guide](../user_guides/install.md), offering a graphical user interface without the need for terminal commands.

A prerequisite for this tutorial is access to one of the supported large language models. Please refer to the [api setup](../user_guides/api_setup.md) for instructions on setting up the API.

Upon successful setup, load your API key with the following two lines:

```py
from dotenv import load_dotenv
load_dotenv()
```

### 2. Create your visualization using different languages

Vizro-AI is versatile, supporting prompts and chart visualizations in multiple languages. Let's explore this capability with two examples, starting with Chinese where we inquire about visualizing the GDP per capita over time.

!!! example "Vizro-AI Chinese"
    === "Code for the cell"
        ```py
        from vizro_ai import VizroAI
        import vizro.plotly.express as px

        from dotenv import load_dotenv
        load_dotenv()

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

        from dotenv import load_dotenv
        load_dotenv()

        df = px.data.gapminder()
        vizro_ai = VizroAI()
        vizro_ai.plot(df, "Visualiere den Trend von der Lebenserwartung in USA über die Jahre im Vergleich zur Veränderung der weltweiten Lebenserwartung über die Jahre und kreiere eine deutsche Visualisierung", explain=True)
        ```
    === "Result"
        [![GermanChart]][GermanChart]

    [GermanChart]: ../../assets/tutorials/chart/GermanExample.png

### 3. Create advanced charts and formatting
Now, let's explore more advanced visualizations and leverage Vizro-AI for enhanced formatting.

To begin, we'll create an animated bar chart illustrating the population development of each continent over time. Let's run the code below and look at the result.

!!! example "Vizro-AI animated chart"
    === "Code for the cell"
        ```py
        from vizro_ai import VizroAI
        import vizro.plotly.express as px

        from dotenv import load_dotenv
        load_dotenv()

        df = px.data.gapminder()
        vizro_ai = VizroAI()
        vizro_ai.plot(df, "The chart should be an animated stacked bar chart with popoluation on the y axis and continent on the x axis with all respective countries, allowing you to observe changes in the population over consecutive years.")
        ```
    === "Result"
        [![AnimatedChart1]][AnimatedChart1]

    [AnimatedChart1]: ../../assets/tutorials/chart/animated_bar_chart_1.png

Having unveiled our animated bar chart showcasing population development per country, it's apparent that crucial details are overshadowed by the legend. Next, we will try to tweak our prompt to group the countries into continents and improve the overall layout.

!!! example "Vizro-AI animated chart"
    === "Code for the cell"
        ```py
        from vizro_ai import VizroAI
        import vizro.plotly.express as px

        from dotenv import load_dotenv
        load_dotenv()

        df = px.data.gapminder()
        vizro_ai = VizroAI()
        vizro_ai.plot(df, "The chart should be an animated stacked bar chart with popoluation on the y axis and continent on the x axis with all respective countries, allowing you to observe changes in the population over consecutive years. Please improve layout.")
        ```
    === "Result"
        [![AnimatedChart2]][AnimatedChart2]

    [AnimatedChart2]: ../../assets/tutorials/chart/animated_bar_chart_2.png


Great, by incorporating the directive `Please improve layout`, we've successfully refined our animation and are now able to better interpret our result.

Now, upon closer inspection, two challenges emerge. Firstly, the legend overlaps the x-axis. Secondly, the y-axis range is insufficient to capture the full spectrum of Asia's population development. Let's run the code below and see how we can improve and finalize our chart.

!!! example "Vizro-AI animated chart"
    === "Code for the cell"
        ```py
        from vizro_ai import VizroAI
        import vizro.plotly.express as px

        from dotenv import load_dotenv
        load_dotenv()

        df = px.data.gapminder()
        vizro_ai = VizroAI()
        vizro_ai.plot(df, "The chart should be an animated stacked bar chart with population on the y axis and continent on the x axis with all respective countries, allowing you to observe changes in the population over consecutive years. Make sure that y axis range fits entire data. Please improve layout and optimize layout of legend.")
        ```
    === "Result"
        [![AnimatedChart3]][AnimatedChart3]

    [AnimatedChart3]: ../../assets/tutorials/chart/animated_bar_chart_3.png

Congratulations! You've now gained insights into harnessing the power of Vizro-AI for crafting advanced charts and elevating formatting. Don't forget, enabling `explain=True` is a good way of learning more about how a chart can be further improved and formatted.
