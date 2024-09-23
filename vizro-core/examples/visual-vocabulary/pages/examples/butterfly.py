import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm
from vizro import Vizro
from vizro.models.types import capture

ages = pd.DataFrame(
    {
        "Age": ["0-19", "20-29", "30-39", "40-49", "50-59", ">=60"],
        "Male": [800, 2000, 4200, 5000, 2100, 800],
        "Female": [1000, 3000, 3500, 3800, 3600, 700],
    }
)


@capture("graph")
def butterfly(data_frame: pd.DataFrame, x1: str, x2: str, y: str):
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=-data_frame[x1],
            y=data_frame[y],
            orientation="h",
            name=x1,
        )
    )
    fig.add_trace(
        go.Bar(
            x=data_frame[x2],
            y=data_frame[y],
            orientation="h",
            name=x2,
        )
    )
    fig.update_layout(barmode="relative")
    return fig


dashboard = vm.Dashboard(
    pages=[
        vm.Page(
            title="Butterfly",
            components=[vm.Graph(figure=butterfly(ages, x1="Male", x2="Female", y="Age"))],
        )
    ]
)
Vizro().build(dashboard).run()
