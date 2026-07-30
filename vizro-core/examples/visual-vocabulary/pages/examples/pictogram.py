import pandas as pd
import plotly.graph_objects as go
from vizro.models.types import capture


@capture("graph")
def pictogram(data_frame: pd.DataFrame, category_col: str, value_col: str) -> go.Figure:
    categories = data_frame[category_col].tolist()
    values = data_frame[value_col].tolist()
    num_categories = len(categories)

    fig = go.Figure()

    for i in range(num_categories):
        cat = categories[i]
        val = int(values[i])
        if val > 0:
            fig.add_trace(
                go.Scatter(
                    x=list(range(val)),
                    y=[num_categories - 1 - i] * val,
                    mode="markers",
                    marker={
                        "size": 16,
                        "color": fig.layout.template.layout.colorway[0],
                    },
                    showlegend=False,
                    hovertemplate=f"{cat}: {val * 100}M<extra></extra>",
                )
            )

    fig.update_yaxes(tickvals=list(range(num_categories)), ticktext=categories[::-1], title="")
    fig.update_xaxes(visible=False, range=[-0.5, max(values) + 0.5])

    return fig


population = pd.DataFrame(
    {
        "country": ["China", "India", "United States", "Indonesia", "Pakistan"],
        "population": [14, 14, 3, 3, 2],
    }
)

fig = pictogram(population, category_col="country", value_col="population")
