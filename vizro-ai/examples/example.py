"""AI plot example."""

import os

import plotly.express as px
import vizro.plotly.express as px
from pydantic_ai.models.openai import OpenAIModel
from vizro_ai import VizroAI

model = OpenAIModel(
    "gpt-4o",
    api_key=os.environ["OPENAI_API_KEY"],
    base_url=os.environ.get("OPENAI_BASE_URL"),
)

vizro_ai = VizroAI(model=model)
df = px.data.gapminder()
fig = vizro_ai.plot(
    df, "describe the composition of gdp in continent,and horizontal line for avg gdp", return_elements=True
)
fig.get_fig_object(df).show()
