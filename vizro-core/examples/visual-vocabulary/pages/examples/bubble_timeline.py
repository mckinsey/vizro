import random

import pandas as pd
import plotly.graph_objects as go
import vizro.plotly.express as px
from vizro.models.types import capture
from vizro.themes import colors
from vizro.themes._palettes import qualitative


@capture("graph")
def bubble_timeline(data_frame: pd.DataFrame) -> go.Figure:
    countries = data_frame["country"].unique().tolist()

    rng = random.Random(42)  # noqa: S311
    jitter = [1 + 0.10 * (2 * rng.random() - 1) for _ in range(len(data_frame))]
    data_frame["_size"] = data_frame["pop"] * jitter

    fig = px.scatter(
        data_frame,
        x="year",
        y="country",
        size="_size",
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

    fig.update_traces(
        marker={"opacity": 0.65, "line": {"width": 0.5, "color": "rgba(255,255,255,0.8)"}},
    )
    fig.update_xaxes(
        title="Year",
        showgrid=False,
        ticklen=4,
        tickfont={"size": 11},
        title_font={"size": 12},
    )
    fig.update_yaxes(
        showgrid=False,
        tickfont={"size": 11},
    )
    fig.update_layout(
        legend={
            "title": "Country",
            "itemsizing": "constant",
            "tracegroupgap": 0,
        },
        margin={"l": 40, "r": 20, "t": 30, "b": 30},
    )

    return fig


gapminder = px.data.gapminder().query("country.isin(['China', 'India', 'United States', 'Indonesia', 'Brazil'])")
fig = bubble_timeline(gapminder)
