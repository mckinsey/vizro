"""AI plot example."""

import os

import logfire
import plotly.express as px
from dotenv import load_dotenv
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

# from vizro_ai import VizroAI
from vizro_ai.agents import chart_agent
from vizro_ai.agents.response_models import BaseChartPlan, ChartPlan, ChartPlanFactory

load_dotenv()

# vizro_ai = VizroAI()
# df = px.data.gapminder()
# fig = vizro_ai.plot(
#     df, "describe the composition of gdp in continent,and horizontal line for avg gdp", return_elements=True
# )
# fig.get_fig_object(df).show()


# # configure logfire
if os.getenv("LOGFIRE_TOKEN"):
    logfire.configure(token=os.getenv("LOGFIRE_TOKEN"))
    logfire.instrument_pydantic_ai()

# User can configure model, including usage limits etc
model = OpenAIChatModel(
    "gpt-4o-mini",
    provider=OpenAIProvider(base_url=os.getenv("OPENAI_BASE_URL"), api_key=os.getenv("OPENAI_API_KEY")),
)
# model = AnthropicModel(
#     "claude-3-7-sonnet-latest",
#     provider=AnthropicProvider(api_key=os.getenv("ANTHROPIC_API_KEY")),
# )

# Get some data
df_iris = px.data.iris()
df_stocks = px.data.stocks()

# Run the agent - user can choose the data_frame
result = chart_agent.run_sync(
    model=model, output_type=ChartPlanFactory(data_frame=df_iris), user_prompt="Create a bar chart", deps=df_iris
)
print(result.output)
# fig = result.output.get_fig_object(df_iris, vizro=True)
# fig.show()
