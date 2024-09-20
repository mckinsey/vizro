"""AI plot example."""

import vizro.plotly.express as px
from vizro_ai import VizroAI

vizro_ai = VizroAI()
df = px.data.gapminder()
fig = vizro_ai.plot(
    df, "describe the composition of gdp in continent,and horizontal line for avg gdp", return_elements=True
)
fig.get_fig_object(df).show()
