"""AI plot example."""

import vizro.plotly.express as px
from dotenv import find_dotenv, load_dotenv
from vizro_ai import VizroAI

load_dotenv(find_dotenv(usecwd=True))
import os

print("LOG LEVEL", os.getenv("VIZRO_AI_LOG_LEVEL"))

vizro_ai = VizroAI()
df = px.data.gapminder()
fig = vizro_ai.plot2(df, "describe the composition of gdp in continent,and horizontal line for avg gdp")
fig.show()
