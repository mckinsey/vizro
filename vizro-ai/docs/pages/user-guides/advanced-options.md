# How to use Vizro-AI's advanced options

This guide shows you how to use the advanced features of the [`chart_agent`][vizro_ai.agents.chart_agent], including working with the [`BaseChartPlan`][vizro_ai.agents.response_models.BaseChartPlan] response model and leveraging Pydantic AI agent capabilities.

## Understanding the response model

When you run `chart_agent.run_sync()` or `chart_agent.run()`, the result contains a [`BaseChartPlan`][vizro_ai.agents.response_models.BaseChartPlan] object in `result.output`. This object contains the generated chart code and metadata.

## BaseChartPlan properties and methods

### `code_vizro` property

Returns the generated chart code formatted for use in Vizro dashboards. The function will include the `@capture("graph")` decorator and use `vizro.plotly.express`.

!!! example "Access the code_vizro property"

    === "Code"

        ```py
        import plotly.express as px
        from pydantic_ai.models.openai import OpenAIChatModel
        from pydantic_ai.providers.openai import OpenAIProvider
        from vizro_ai.agents import chart_agent

        model = OpenAIChatModel(
            "gpt-5-nano-2025-08-07",
            provider=OpenAIProvider(api_key="your-api-key-here"),
        )

        df = px.data.gapminder()
        result = chart_agent.run_sync(
            model=model,
            user_prompt="the trend of gdp over years in the US",
            deps=df,
        )
        print(result.output.code_vizro)
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

### `code` property

Returns the generated chart code as a pure Plotly code string. The function will be named `custom_chart`.

!!! example "Access the code property"

    === "Code"

        ```py
        import plotly.express as px
        from pydantic_ai.models.openai import OpenAIChatModel
        from pydantic_ai.providers.openai import OpenAIProvider
        from vizro_ai.agents import chart_agent

        model = OpenAIChatModel(
            "gpt-5-nano-2025-08-07",
            provider=OpenAIProvider(api_key="your-api-key-here"),
        )

        df = px.data.gapminder()
        result = chart_agent.run_sync(
            model=model,
            user_prompt="the trend of gdp over years in the US",
            deps=df,
        )
        print(result.output.code)
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

### `get_fig_object()` method

Executes the generated code to create a Plotly figure object. Note that this dynamically executes code - be sure [to read and understand what it means when dynamically generated code is executed](../explanation/safety-in-vizro-ai.md#execution-of-dynamic-code-in-vizro-ai).

**Parameters:**

- `data_frame`: The pandas DataFrame to use for generating the chart
- `chart_name`: Optional name for the chart function (defaults to `custom_chart`)
- `vizro`: Whether to generate Vizro-compatible code (defaults to `False`)

!!! note "Requirements for `vizro=True`"
    By default, `get_fig_object()` generates a pure Plotly figure object. If you would like to generate a Vizro-compatible figure that also has the Vizro theming, you can set `vizro=True` but you need to ensure that `vizro` is installed: `pip install vizro` or `pip install vizro-ai[vizro]`. More on this topic in our guide on [how to add your Vizro-AI charts to a Vizro dashboard](add-generated-chart-usecase.md).

#### Vizro-ready figure

The `fig` object (with `vizro=True`) is in the standard `vizro_dark` theme, and can [be inserted into a Vizro dashboard](add-generated-chart-usecase.md).

!!! example "Get Vizro-ready figure"

    === "Code"

        ```py
        import plotly.express as px
        from pydantic_ai.models.openai import OpenAIChatModel
        from pydantic_ai.providers.openai import OpenAIProvider
        from vizro_ai.agents import chart_agent

        model = OpenAIChatModel(
            "gpt-5-nano-2025-08-07",
            provider=OpenAIProvider(api_key="your-api-key-here"),
        )

        df = px.data.gapminder()
        result = chart_agent.run_sync(
            model=model,
            user_prompt="the trend of gdp over years in the US",
            deps=df,
        )
        fig = result.output.get_fig_object(data_frame=df, vizro=True)
        fig.show()
        ```

    === "Result"

        [![VizroAIChartVizro]][vizroaichartvizro]

#### Pure Plotly figure

Otherwise, the `fig` object is a basic plotly figure without Vizro theming.

!!! example "Get pure Plotly figure"

    === "Code"

        ```py
        import plotly.express as px
        from pydantic_ai.models.openai import OpenAIChatModel
        from pydantic_ai.providers.openai import OpenAIProvider
        from vizro_ai.agents import chart_agent

        model = OpenAIChatModel(
            "gpt-5-nano-2025-08-07",
            provider=OpenAIProvider(api_key="your-api-key-here"),
        )

        df = px.data.gapminder()
        result = chart_agent.run_sync(
            model=model,
            user_prompt="the trend of gdp over years in the US",
            deps=df,
        )
        fig = result.output.get_fig_object(data_frame=df)
        fig.show()
        ```

    === "Result"

        [![VizroAIChartPlotly]][vizroaichartplotly]

#### Using different data

You can create the `fig` object with different data while ensuring the overall schema remains consistent. You can re-evaluate this function to generate various `fig` objects for different data. For example, the code could be generated using fake or sample data fed into Vizro-AI. When moving to production, you can switch the data source to the complete dataset, as long as the data schema is consistent.

!!! example "Use different data"

    === "Code"

        ```py
        import plotly.express as px
        from pydantic_ai.models.openai import OpenAIChatModel
        from pydantic_ai.providers.openai import OpenAIProvider
        from vizro_ai.agents import chart_agent

        model = OpenAIChatModel(
            "gpt-5-nano-2025-08-07",
            provider=OpenAIProvider(api_key="your-api-key-here"),
        )

        df = px.data.gapminder()
        result = chart_agent.run_sync(
            model=model,
            user_prompt="the average of gdp for all continents as bar chart",
            deps=df,
        )

        # The produced chart could handle many continents, but we choose to filter for the US
        df_us = df[df['country'] == 'United States']
        fig = result.output.get_fig_object(chart_name="different_name", data_frame=df_us, vizro=True)
        fig.show()
        ```

    === "Result"

        [![VizroAINewData]][vizroainewdata]

#### Changing the chart name

This option executes the chart code with the name given under `chart_name`. This can be important when you want to avoid overwriting variables in the namespace.

!!! example "Change the chart name"

    === "Code"

        ```py
        import plotly.express as px
        from pydantic_ai.models.openai import OpenAIChatModel
        from pydantic_ai.providers.openai import OpenAIProvider
        from vizro_ai.agents import chart_agent

        model = OpenAIChatModel(
            "gpt-5-nano-2025-08-07",
            provider=OpenAIProvider(api_key="your-api-key-here"),
        )

        df = px.data.gapminder()
        result = chart_agent.run_sync(
            model=model,
            user_prompt="the trend of gdp over years in the US",
            deps=df,
        )
        fig = result.output.get_fig_object(chart_name="different_name", data_frame=df, vizro=True)
        print(fig._captured_callable._function)
        ```

    === "Result"

        ```py
        <function different_name at 0x17a18df80>
        ```

## Alternative response models

You can also use [`ChartPlan`][vizro_ai.agents.response_models.ChartPlan] or a model created by [`ChartPlanFactory`][vizro_ai.agents.response_models.ChartPlanFactory] as output types. `ChartPlan` extends `BaseChartPlan` with additional explanatory fields like `chart_insights` and `code_explanation`. `ChartPlanFactory` creates a dynamically validated model class that tests code execution before accepting the response.

```py
from vizro_ai.agents import chart_agent
from vizro_ai.agents.response_models import ChartPlan, ChartPlanFactory
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
import plotly.express as px

df = px.data.gapminder()
model = OpenAIChatModel("gpt-5-nano-2025-08-07", provider=OpenAIProvider(api_key="your-api-key-here"))
result = chart_agent.run_sync(model=model, user_prompt="create a bar chart", deps=df, output_type=ChartPlan)
print(result.output.chart_insights)
```

## Pydantic-AI agent capabilities

Since `chart_agent` is a Pydantic AI agent, you can leverage all Pydantic AI features:

### Async execution

Use `chart_agent.run()` for async execution:

```py
import asyncio
import plotly.express as px
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from vizro_ai.agents import chart_agent

model = OpenAIChatModel("gpt-5-nano-2025-08-07", provider=OpenAIProvider(api_key="your-api-key-here"))
df = px.data.gapminder()

async def main():
    result = await chart_agent.run(
        model=model,
        user_prompt="create a bar chart",
        deps=df,
    )
    fig = result.output.get_fig_object(df, vizro=True)
    fig.show()

if __name__ == "__main__":
    asyncio.run(main())
```

### Streaming

Stream responses as they're generated:

```py
import asyncio
import plotly.express as px
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from vizro_ai.agents import chart_agent

model = OpenAIChatModel("gpt-5-nano-2025-08-07", provider=OpenAIProvider(api_key="your-api-key-here"))
df = px.data.gapminder()

async def main():
    async with chart_agent.run_stream(
        model=model,
        user_prompt="create a bar chart",
        deps=df,
    ) as response:
        async for text in response.stream_output():
            print(text)
        result = await response.get_output()
    fig = result.get_fig_object(df, vizro=True)
    fig.show()

if __name__ == "__main__":
    asyncio.run(main())
```

### Dependency injection

The `deps` parameter allows you to inject any dependency (in this case, the DataFrame). This enables flexible data handling and can be extended for more complex use cases. See the [Pydantic AI documentation](https://ai.pydantic.dev/agents/) for more details.

### Custom instructions and tools

You can extend the `chart_agent` with custom instructions and tools, just like any Pydantic AI agent. See the [Pydantic AI documentation](https://ai.pydantic.dev/agents/) for more details.

### Web Chat UI

You can create an interactive web chat interface for `chart_agent` using Pydantic AI's built-in Web Chat UI. Install the extra:

```bash
pip install 'pydantic-ai-slim[web]'
```

!!! example "Create a web chat interface"

    ```py
    from vizro_ai.agents import chart_agent

    app = chart_agent.to_web()
    ```

    Run the app with any ASGI server:

    ```bash
    uvicorn my_module:app --host 127.0.0.1 --port 7932
    ```

For more details, see the [Pydantic AI Web Chat UI documentation](https://ai.pydantic.dev/web/).

### Agent2Agent (A2A) protocol

The `chart_agent` can participate in agent-to-agent workflows using the A2A protocol.

!!! example "Use chart_agent in an A2A workflow"

    ```py
    from vizro_ai.agents import chart_agent

    app = chart_agent.to_a2a()
    ```

For more details, see the [Pydantic AI A2A protocol documentation](https://ai.pydantic.dev/a2a/).

## Learn more

For more information on Pydantic AI agent capabilities, see the [Pydantic AI agents documentation](https://ai.pydantic.dev/agents/).

[vizroaichartplotly]: ../../assets/user_guides/VizroAIPlotly.png
[vizroaichartvizro]: ../../assets/user_guides/VizroAIVizro.png
[vizroainewdata]: ../../assets/user_guides/VizroAINewData.png
