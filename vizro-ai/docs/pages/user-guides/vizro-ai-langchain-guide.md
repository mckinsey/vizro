# Using Vizro-AI Methods as LangChain Tools

This guide demonstrates how to integrate Vizro-AI's plotting and dashboard generation capabilities with LangChain tools. This integration allows you to use Vizro-AI's functionality within a larger LangChain application.

## 1. Set up the environment

First, import the required libraries and prepare your data:

```python
from copy import deepcopy
from typing import Annotated, Any

import pandas as pd
import vizro.plotly.express as px
from langchain_core.runnables import chain
from langchain_core.tools import InjectedToolArg, tool
from langchain_openai import ChatOpenAI
from vizro_ai import VizroAI

# Load sample data
df = px.data.gapminder()
dfs = [df]

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o-mini")
```

## 2. Define LangChain tools

Basic tools only take string as input and output. Vizro-AI takes Pandas dataframes as input and it's not cost-efficient and secure to pass the full dataset to a LLM. In this case, [bind the Pandas dataframes at run time](https://python.langchain.com/v0.2/docs/how_to/tool_runtime/) is more suitable.

Now, create tools that wrap Vizro-AI's plotting and dashboard generation capabilities:

```python
@tool(parse_docstring=True)
def get_plot_code(df: Annotated[Any, InjectedToolArg], question: str) -> str:
    """Generate only the plot code.

    Args:
        df: A pandas DataFrame
        question: The plotting question

    Returns:
        Generated plot code
    """
    df = pd.DataFrame(df)
    vizro_ai = VizroAI(model=llm)
    plot_elements = vizro_ai.plot(
        df,
        user_input=question,
        return_elements=True,
    )
    return plot_elements.code_vizro

@tool(parse_docstring=True)
def get_dashboard_code(dfs: Annotated[Any, InjectedToolArg], question: str) -> str:
    """Generate the dashboard code.

    Args:
        dfs: Pandas DataFrames
        question: The dashboard question

    Returns:
        Generated dashboard code
    """
    vizro_ai = VizroAI(model=llm)
    dashboard_elements = vizro_ai.dashboard(
        dfs,
        user_input=question,
        return_elements=True,
    )
    return dashboard_elements.code
```

## 3. Set up the tool chain

Create a chain that handles tool execution and data injection:

```python
# Bind tools to the LLM
tools = [get_plot_code, get_dashboard_code]
llm_with_tools = llm.bind_tools(tools)

# Create data injection chain
@chain
def inject_df(ai_msg):
    tool_calls = []
    for tool_call in ai_msg.tool_calls:
        tool_call_copy = deepcopy(tool_call)

        if tool_call_copy["name"] == "get_dashboard_code":
            tool_call_copy["args"]["dfs"] = dfs
        else:
            tool_call_copy["args"]["df"] = df

        tool_calls.append(tool_call_copy)
    return tool_calls

# Create tool router
tool_map = {tool.name: tool for tool in tools}

@chain
def tool_router(tool_call):
    return tool_map[tool_call["name"]]

# Combine chains
chain = llm_with_tools | inject_df | tool_router.map()
```

## 4. Use the chain

Now you can use the chain to generate plots or dashboards based on natural language queries. The chain will generate code that you can use to create visualizations.

!!! example "Generate plot code"

    === "Code"
        ```py
        plot_response = chain.invoke("Plot GDP per capita for each continent")
        print(plot_response[0].content)
        ```
    === "Vizro-AI Generated Code"
        ```py
        import plotly.graph_objects as go
        from vizro.models.types import capture

        @capture("graph")
        def custom_chart(data_frame):
            continent_gdp = data_frame.groupby("continent")["gdpPercap"].mean().reset_index()
            fig = go.Figure(
                data=[go.Bar(x=continent_gdp["continent"], y=continent_gdp["gdpPercap"])]
            )
            fig.update_layout(
                title="GDP per Capita by Continent",
                xaxis_title="Continent",
                yaxis_title="GDP per Capita",
            )
            return fig
        ```

!!! example "Generate dashboard code"

    === "Code"
        ```py
        dashboard_response = chain.invoke("Create a dashboard. This dashboard has a chart showing the correlation between gdpPercap and lifeExp.")
        print(dashboard_response[0].content)
        ```
    === "Vizro-AI Generated Code"
        ```py
        ############ Imports ##############
        import vizro.models as vm
        from vizro.models.types import capture
        import plotly.graph_objects as go


        ####### Function definitions ######
        @capture("graph")
        def gdp_life_exp_graph(data_frame):
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(x=data_frame["gdpPercap"], y=data_frame["lifeExp"], mode="markers")
            )
            fig.update_layout(
                title="GDP per Capita vs Life Expectancy",
                xaxis_title="GDP per Capita",
                yaxis_title="Life Expectancy",
            )
            return fig


        ####### Data Manager Settings #####
        #######!!! UNCOMMENT BELOW !!!#####
        # from vizro.managers import data_manager
        # data_manager["gdp_life_exp"] = ===> Fill in here <===


        ########### Model code ############
        model = vm.Dashboard(
            pages=[
                vm.Page(
                    components=[
                        vm.Graph(
                            id="gdp_life_exp_graph",
                            figure=gdp_life_exp_graph(data_frame="gdp_life_exp"),
                        )
                    ],
                    title="GDP vs Life Expectancy Correlation",
                    layout=vm.Layout(grid=[[0]]),
                    controls=[],
                )
            ],
            title="GDP per Capita vs Life Expectancy",
        )
        ```

This integration allows you to leverage Vizro-AI's visualization capabilities within a LangChain application, enabling natural language-driven creation of plots and dashboards.
