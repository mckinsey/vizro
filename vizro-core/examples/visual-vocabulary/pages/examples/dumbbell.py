import pandas as pd
import plotly.graph_objects as go
import vizro.plotly.express as px
from vizro.models.types import capture


@capture("graph")
def dumbbell(data_frame: pd.DataFrame, **kwargs) -> go.Figure:
    fig = px.scatter(data_frame, **kwargs)

    orientation = fig.data[0].orientation
    x_or_y = "x" if orientation == "h" else "y"
    y_or_x = "y" if orientation == "h" else "x"

    for x_or_y_0, x_or_y_1, y_or_x_0, y_or_x_1 in zip(
        fig.data[0][x_or_y],
        fig.data[1][x_or_y],
        fig.data[0][y_or_x],
        fig.data[1][y_or_x],
    ):
        fig.add_shape(
            **{f"{x_or_y}0": x_or_y_0, f"{x_or_y}1": x_or_y_1, f"{y_or_x}0": y_or_x_0, f"{y_or_x}1": y_or_x_1},
            type="line",
            layer="below",
            line_color="grey",
            line_width=3,
        )

    fig.update_traces(marker_size=12)
    return fig


salaries = pd.DataFrame(
    {
        "Job": ["Developer", "Analyst", "Manager", "Specialist"],
        "Min": [60000, 55000, 70000, 50000],
        "Max": [130000, 110000, 96400, 80000],
    }
)

fig = dumbbell(salaries, y="Job", x=["Min", "Max"], labels={"variable": "", "value": "Salary in $"})
