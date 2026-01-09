"""AI plot example."""

import os

import logfire
import plotly.express as px
from dotenv import load_dotenv
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from vizro_ai.agents import chart_agent

load_dotenv()

# Configure logfire for observability if desired
if os.getenv("LOGFIRE_TOKEN"):
    logfire.configure(token=os.getenv("LOGFIRE_TOKEN"))
    logfire.instrument_pydantic_ai()

# User can configure model, including usage limits etc
model = OpenAIChatModel(
    "gpt-5-nano-2025-08-07",
    provider=OpenAIProvider(base_url=os.getenv("OPENAI_BASE_URL"), api_key=os.getenv("OPENAI_API_KEY")),
)
# model = AnthropicModel(
#     "claude-3-7-sonnet-latest",
#     provider=AnthropicProvider(api_key=os.getenv("ANTHROPIC_API_KEY")),
# )

# Get some data
df_iris = px.data.iris()

# Run the agent - user can choose the data_frame
result = chart_agent.run_sync(model=model, user_prompt="Create a bar chart", deps=df_iris)
fig = result.output.get_fig_object(df_iris, vizro=True)
fig.show()
