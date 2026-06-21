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
        val = values[i]
        if val > 0:
            fig.add_trace(
                go.Scatter(
                    x=list(range(val)),
                    y=[num_categories - 1 - i] * val,
                    mode="markers",
                    marker={
                        "symbol": "circle",
                        "size": 16,
                        "color": "#009FE3",
                        "line": {"color": "#0078B3", "width": 1},
                    },
                    showlegend=False,
                    hovertemplate=f"{cat}: {val * 100}M<extra></extra>",
                )
            )

    fig.update_yaxes(tickvals=list(range(num_categories)), ticktext=categories[::-1], title="")
    fig.update_xaxes(visible=False, range=[-0.5, max(values) + 0.5])
    fig.update_layout(height=400, plot_bgcolor="white", margin={"l": 0, "r": 0, "t": 0, "b": 0})

    return fig


population = pd.DataFrame(
    {
        "country": ["China", "India", "United States", "Indonesia", "Pakistan"],
        "population": [14, 14, 3, 3, 2],
    }
)

fig = pictogram(population, category_col="country", value_col="population")
