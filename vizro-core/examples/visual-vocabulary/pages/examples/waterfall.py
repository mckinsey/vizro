import pandas as pd
import plotly.graph_objects as go
from vizro.models.types import capture


@capture("graph")
def waterfall(
    data_frame: pd.DataFrame,
    x: str,
    y: str,
    measure: list[str],
):
    return go.Figure(
        data=go.Waterfall(x=data_frame[x], y=data_frame[y], measure=data_frame[measure]),
        layout={"showlegend": False},
    )


waterfall_data = pd.DataFrame(
    {
        "x": ["Sales", "Consulting", "Net revenue", "Purchases", "Other expenses", "Profit before tax"],
        "y": [60, 80, 0, -40, -20, 0],
        "measure": ["relative", "relative", "total", "relative", "relative", "total"],
    }
)

fig = waterfall(waterfall_data, x="x", y="y", measure="measure")
