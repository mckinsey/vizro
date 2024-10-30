import pandas as pd
import plotly.graph_objects as go
import vizro.plotly.express as px
from vizro.models.types import capture


@capture("graph")
def categorical_column(data_frame: pd.DataFrame, **kwargs) -> go.Figure:
    fig = px.bar(data_frame, **kwargs)
    fig.update_xaxes(type="category")
    return fig


gapminder = px.data.gapminder().query("country == 'Nigeria' and year > 1970")

fig = categorical_column(gapminder, x="year", y="lifeExp")
