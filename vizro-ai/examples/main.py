import os

import plotly.express as px
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.openai import OpenAIProvider
from vizro_ai.agents._chart_agent import chart_agent

df = px.data.iris()

model1 = OpenAIChatModel(
    "gpt-4o-mini",
    provider=OpenAIProvider(base_url=os.getenv("OPENAI_BASE_URL"), api_key=os.getenv("OPENAI_API_KEY")),
)
model2 = AnthropicModel(
    "claude-3-7-sonnet-latest",
    provider=AnthropicProvider(api_key=os.getenv("ANTHROPIC_API_KEY")),
)

app = chart_agent.to_web(models={"GPT 5": model1, "Claude": model2}, deps=df)
