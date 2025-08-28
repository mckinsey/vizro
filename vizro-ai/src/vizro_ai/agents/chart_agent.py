import asyncio
import os

import logfire
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.openai import OpenAIProvider

from vizro_ai.plot._response_models import BaseChartPlan, ChartPlan, ChartPlanFactory

# from vizro_ai.plot._response_models import BaseChartPlan, ChartPlan, ChartPlanFactory

chart_agent = Agent(
    deps_type=pd.DataFrame,
    output_type=BaseChartPlan,  # ChartPlanFactory(df),
    instructions=(
        "You are an expert in data visualization. You are given a user request and you need to generate chart code."
    ),
)


@chart_agent.instructions
def add_df(ctx: RunContext[pd.DataFrame]) -> str:
    """Add the dataframe to the chart plan."""
    return f"A sample of the data is {ctx.deps.sample(5)}"


if __name__ == "__main__":
    load_dotenv()
    # configure logfire
    logfire.configure(token=os.getenv("LOGFIRE_TOKEN"))
    logfire.instrument_pydantic_ai()

    # User can configure model, including usage limits etc
    # model = OpenAIModel(
    #     "gpt-4o-mini",
    #     provider=OpenAIProvider(base_url=os.getenv("OPENAI_BASE_URL"), api_key=os.getenv("OPENAI_API_KEY")),
    # )
    model = AnthropicModel(
        "claude-3-7-sonnet-latest",
        provider=AnthropicProvider(api_key=os.getenv("ANTHROPIC_API_KEY")),
    )

    # Get some data
    df_iris = px.data.iris()
    df_stocks = px.data.stocks()

    # Run the agent - user can choose the data_frame
    # result = chart_agent.run_sync(model=model, user_prompt="Create a bar chart", deps=df_stocks)
    # print(result.output.chart_code)

    # async def main():
    #     async with chart_agent.run_stream(
    #         model=model, user_prompt="Create a bar chart of the iris dataset."
    #     ) as response:
    #         async for text in response.stream():
    #             print(text)

    # asyncio.run(main())

    #### Test code execution
    from pydantic_ai import CodeExecutionTool

    agent = Agent(model=model, builtin_tools=[CodeExecutionTool()])

    result = agent.run_sync("Calculate the factorial of 15 and show your work")
    print(result)
    # I am not sure the model actually uses the inbuilt tool...
