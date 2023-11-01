"""AI plot example."""
import plotly.express as px
from vizro_ai import VizroAI

vizro_ai = VizroAI()
df = px.data.gapminder()
vizro_ai.plot(df, "describe the composition of gdp in continent,and horizontal line for avg gdp")
