# How to use Vizro-AI's advanced options

This guide shows you how to use the advanced options of `VizroAI.plot`.

First we show how to change the input parameters of the function, as follows:

- control over whether code gets executed,
- the number of retries of `.plot` when it fails validation,
- how to request a comprehensive output (when `return_elements=True`).

Second we show how to use this more comprehensive output, enabling control of code generation and `fig` object production.

## Inputs of `VizroAI.plot`

### `user_input`

This is the natural language query from which, together with a data sample, the LLM creates a plotly chart. For the query, you can [use English or a different language](use-different-languages.md). The complexity of the resulting chart [depends on the vendor model capabilities](customize-vizro-ai.md#what-model-to-choose).

### `df`

Supply any `pandas` data frame to base your query on. The LLM will receive a sample of this data frame to form an appropriate graph.

If the option `validate_code` is set to `True` (which it is by default), the LLM created chart code will be evaluated on a sample of this data frame.

If `return_elements` is set to `False`, then the returned `fig` object will be created based on this (entire) data frame.

<!-- vale off -->

### `max_debug_retry`

This number determines how often the tool will try to correct an incorrect response (that fails various validation criteria). Under the hood this is [implemented via pydantic validators](https://docs.pydantic.dev/1.10/usage/validators/). The last response will be re-sent to the LLM together with the validation error(s) in order to receive an improved response. This concept is [inspired by the amazing instructor library](https://github.com/jxnl/instructor).

### `return_elements`

This boolean (by default `False`) determines the return type of `VizroAI.plot`.

If set to `False`, then dynamically generated Python code is executed to produce a `plotly.graph_objects.Figure` object from the LLM response and the user supplied data frame. Strictly speaking, it produces a `vizro.charts._charts_utils._DashboardReadyFigure`, which behaves essentially like the former, but is ready to be [inserted](add-generated-chart-usecase.md) into a [Vizro](https://vizro.readthedocs.io/en/stable/) dashboard. It also comes with the default Vizro dark theme.

If set to `True`, a class (pydantic model) is returned from which the `fig` object, but also various other outputs can be generated. (see below)

### `validate_code`

This boolean (by default `True`) determines whether the LLM generated Python code executes with a sample of the data in order to verify that it runs and produces a plotly figure. Be sure [to read and understand what it means when dynamically generated code is executed](../explanation/safety-in-vizro-ai.md#execution-of-dynamic-code-in-vizro-ai).

<!-- vale on -->

If `return_elements=True` **and** `validate_code=False`, then no code is executed to obtain the return of `VizroAI.plot`. This means that the code string obtained is not validated, but also that no code was executed.

## Output if `return_elements=True`

If `return_elements=True`, then instead of a `fig` object, a class is returned, which enables the following options:

### Obtain `vizro` code string

You can obtain the code string that would produce the answer to the user query as a Vizro dashboard ready figure as follows. The name for the function will be `custom_chart`:

!!! example "Vizro code"

    === "Code"

        ```py
        from vizro_ai import VizroAI
        import plotly.express as px

        df = px.data.gapminder()
        vizro_ai = VizroAI()

        res = vizro_ai.plot(df, "the trend of gdp over years in the US", return_elements=True)
        print(res.code_vizro)
        ```

    === "Result"

        ```py
        import vizro.plotly.express as px
        from vizro.models.types import capture


        @capture("graph")
        def custom_chart(data_frame):
            us_data = data_frame[data_frame["country"] == "United States"]
            fig = px.line(
                us_data, x="year", y="gdpPercap", title="GDP per Capita Over Years in the US"
            )
            return fig
        ```

### Obtain `plotly` code string

You can obtain the code string that would produce the answer to the user query as a pure `plotly.graph_objects.Figure` as follows. The name for the function will be `custom_chart`:

!!! example "Plotly code"

    === "Code"

        ```py
        from vizro_ai import VizroAI
        import plotly.express as px

        df = px.data.gapminder()
        vizro_ai = VizroAI()

        res = vizro_ai.plot(df, "the trend of gdp over years in the US", return_elements=True)
        print(res.code)
        ```

    === "Result"

        ```py
        import plotly.express as px


        def custom_chart(data_frame):
            us_data = data_frame[data_frame["country"] == "United States"]
            fig = px.line(
                us_data, x="year", y="gdpPercap", title="GDP per Capita Over Years in the US"
            )
            return fig
        ```

### Obtain `fig` object

You can create the `fig` object using either of the above produced code strings (vizro or plotly), changing the chart name, and using different data. Note that when executing this function, the produced code string will be dynamically executed. Be sure [to read and understand what it means when dynamically generated code is executed](../explanation/safety-in-vizro-ai.md#execution-of-dynamic-code-in-vizro-ai).

#### Vizro ready

This `fig` object is in the standard `vizro_dark` theme, and can [be inserted into a Vizro dashboard](add-generated-chart-usecase.md).

!!! example "Vizro `fig` object"

    === "Code"

        ```py
        from vizro_ai import VizroAI
        import plotly.express as px

        df = px.data.gapminder()
        vizro_ai = VizroAI()

        res = vizro_ai.plot(df, "the trend of gdp over years in the US", return_elements=True)
        fig = res.get_fig_object(data_frame=df, vizro=True)
        fig.show()
        ```

    === "Result"

        [![VizroAIChartVizro]][vizroaichartvizro]

#### Pure Plotly/Dash

This `fig` object is a basic plotly figure.

!!! example "Plotly `fig` object"

    === "Code"

        ```py
        from vizro_ai import VizroAI
        import plotly.express as px

        df = px.data.gapminder()
        vizro_ai = VizroAI()

        res = vizro_ai.plot(df, "the trend of gdp over years in the US", return_elements=True)
        fig = res.get_fig_object(data_frame=df, vizro=False)
        fig.show()
        ```

    === "Result"

        [![VizroAIChartPlotly]][vizroaichartplotly]

#### Using different data

<!--vale off-->

You can create the `fig` object with different data while ensuring the overall schema remains consistent. You can re-evaluate this function to generate various `fig` objects for different data. For example, the code could be generated using fake or sample data fed into Vizro-AI. When moving to production, you can switch the data source to the complete dataset, as long as the data schema is consistent.

<!--vale on-->

!!! example "Different data"

    === "Code"

        ```py
        from vizro_ai import VizroAI
        import plotly.express as px

        df = px.data.gapminder()
        vizro_ai = VizroAI()

        res = vizro_ai.plot(df, "the average of gdp for all continents as bar chart", return_elements=True)

        # The produced chart could handle many continents, but we choose to filter for the US
        df_us = df[df['country'] == 'United States']
        fig = res.get_fig_object(chart_name="different_name", data_frame=df_us, vizro=True)
        fig.show()
        ```

    === "Result"

        [![VizroAINewData]][vizroainewdata]

#### Changing the chart name

This option executes the chart code with the name given under `chart_name`. This can be important when you want to avoid overwriting variables in the namespace.

!!! example "Changing the `chart_name`"

    === "Code"

        ```py
        from vizro_ai import VizroAI
        import plotly.express as px

        df = px.data.gapminder()
        vizro_ai = VizroAI()

        res = vizro_ai.plot(df, "the trend of gdp over years in the US", return_elements=True)
        fig = res.get_fig_object(chart_name="different_name",data_frame=df, vizro=True)
        print(fig._captured_callable._function)
        ```

    === "Result"

        ```py
        <function different_name at 0x17a18df80>
        ```

[vizroaichartplotly]: ../../assets/user_guides/VizroAIPlotly.png
[vizroaichartvizro]: ../../assets/user_guides/VizroAIVizro.png
[vizroainewdata]: ../../assets/user_guides/VizroAINewData.png
