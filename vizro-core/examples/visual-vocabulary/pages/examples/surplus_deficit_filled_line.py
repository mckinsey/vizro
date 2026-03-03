import numpy as np
import pandas as pd
import plotly.graph_objects as go
from vizro.models.types import capture


@capture("graph")
def surplus_deficit_filled_line(
    data_frame: pd.DataFrame,
    x: str,
    y: str,
) -> go.Figure:
    x_data = data_frame[x]
    y_data = data_frame[y]

    fig = go.Figure()

    # Create surplus (positive) filled area
    y_surplus = np.where(y_data >= 0, y_data, 0)
    fig.add_trace(
        go.Scatter(
            x=x_data,
            y=y_surplus,
            fill="tozeroy",
            mode="none",
            name="Surplus",
        )
    )

    # Create deficit (negative) filled area
    y_deficit = np.where(y_data <= 0, y_data, 0)
    fig.add_trace(
        go.Scatter(
            x=x_data,
            y=y_deficit,
            fill="tozeroy",
            mode="none",
            name="Deficit",
        )
    )

    # Add the actual line on top
    fig.add_trace(
        go.Scatter(
            x=x_data,
            y=y_data,
            mode="lines",
            line={"color": "black", "width": 2},
            showlegend=False,
        )
    )

    # Add a zero baseline
    fig.add_hline(y=0, line_width=1, line_color="grey", line_dash="dash")

    return fig


surplus_deficit_data = pd.DataFrame(
    {
        "Month": [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ],
        "Balance": [4, -2, 3, 5, -1, -4, 2, 6, -3, 1, -5, 3],
    }
)

fig = surplus_deficit_filled_line(surplus_deficit_data, x="Month", y="Balance")
