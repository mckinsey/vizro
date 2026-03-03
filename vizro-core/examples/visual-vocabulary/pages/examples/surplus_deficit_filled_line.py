import numpy as np
import pandas as pd
import plotly.graph_objects as go
from vizro.models.types import capture


@capture("graph")
def surplus_deficit_filled_line(data_frame: pd.DataFrame, x: str, y: str) -> go.Figure:
    x_labels = data_frame[x].values
    y_vals = data_frame[y].values.astype(float)
    x_idx = np.arange(len(y_vals), dtype=float)

    # Build x/y arrays with zero-crossing points inserted so filled areas
    # meet y=0 exactly where the line crosses, not at the next data point.
    xs, ys = [x_idx[0]], [y_vals[0]]
    for i in range(1, len(y_vals)):
        if y_vals[i - 1] * y_vals[i] < 0:
            frac = -y_vals[i - 1] / (y_vals[i] - y_vals[i - 1])
            xs.append(x_idx[i - 1] + frac)
            ys.append(0.0)
        xs.append(x_idx[i])
        ys.append(y_vals[i])
    xs, ys = np.array(xs), np.array(ys)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=np.where(ys >= 0, ys, 0), fill="tozeroy", mode="none"))
    fig.add_trace(go.Scatter(x=xs, y=np.where(ys <= 0, ys, 0), fill="tozeroy", mode="none"))
    fig.update_xaxes(tickvals=x_idx, ticktext=x_labels)
    fig.update_layout(showlegend=False)
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
