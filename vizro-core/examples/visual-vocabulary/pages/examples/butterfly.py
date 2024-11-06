import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from vizro.models.types import capture


@capture("graph")
def butterfly(data_frame: pd.DataFrame, **kwargs) -> go.Figure:
    fig = px.bar(data_frame, **kwargs)

    orientation = fig.data[0].orientation
    x_or_y = "x" if orientation == "h" else "y"

    fig.update_traces({f"{x_or_y}axis": f"{x_or_y}2"}, selector=1)
    fig.update_layout({f"{x_or_y}axis2": fig.layout[f"{x_or_y}axis"]})
    fig.update_layout(
        {f"{x_or_y}axis": {"autorange": "reversed", "domain": [0, 0.5]}, f"{x_or_y}axis2": {"domain": [0.5, 1]}}
    )

    if orientation == "h":
        fig.add_vline(x=0, line_width=2, line_color="grey")
    else:
        fig.add_hline(y=0, line_width=2, line_color="grey")

    return fig


ages = pd.DataFrame(
    {
        "Age": ["0-19", "20-29", "30-39", "40-49", "50-59", ">=60"],
        "Male": [800, 2000, 4200, 5000, 2100, 800],
        "Female": [1000, 3000, 3500, 3800, 3600, 700],
    }
)

fig = butterfly(ages, x=["Male", "Female"], y="Age", labels={"value": "Population", "variable": "Sex"})
