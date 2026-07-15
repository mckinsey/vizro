import pandas as pd
import plotly.graph_objects as go
import vizro.plotly.express as px
from vizro.models.types import capture
from vizro.themes import colors
from vizro.themes._palettes import qualitative


@capture("graph")
def bubble_timeline(data_frame: pd.DataFrame) -> go.Figure:
    countries = data_frame["country"].unique().tolist()

    fig = px.scatter(
        data_frame,
        x="year",
        y="country",
        size="pop",
        color="country",
        color_discrete_sequence=qualitative,
        size_max=28,
        category_orders={"country": countries},
        hover_name="country",
    )

    for country, country_data in data_frame.groupby("country"):
        fig.add_shape(
            type="line",
            x0=country_data["year"].min(),
            y0=country,
            x1=country_data["year"].max(),
            y1=country,
            line={"color": colors.gray_400, "width": 1},
            layer="below",
        )

    fig.update_xaxes(title="Year", showgrid=False)
    fig.update_yaxes(showgrid=False)
    fig.update_layout(
        legend={
            "title": "Country",
            "itemsizing": "constant",
        },
    )

    return fig


gapminder = px.data.gapminder().query("country.isin(['China', 'India', 'United States', 'Indonesia', 'Brazil'])")
fig = bubble_timeline(gapminder)
