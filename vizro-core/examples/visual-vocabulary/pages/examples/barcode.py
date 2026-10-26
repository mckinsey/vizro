import pandas as pd
import plotly.graph_objects as go
import vizro.plotly.express as px
from vizro.models.types import capture


@capture("graph")
def barcode(data_frame: pd.DataFrame, x: str) -> go.Figure:
    """Create a barcode plot with one vertical mark per observation."""
    axis_title = x.replace("_", " ").title()
    fig = go.Figure(
        go.Scatter(
            x=data_frame[x],
            y=[0] * len(data_frame),
            mode="markers",
            marker={"symbol": "line-ns-open", "size": 24, "line": {"width": 2}},
            showlegend=False,
            hovertemplate=f"{axis_title}: %{{x}}<extra></extra>",
        )
    )
    fig.update_xaxes(title=axis_title, showgrid=False, zeroline=False)
    fig.update_yaxes(visible=False, range=[-0.5, 0.5], fixedrange=True)
    return fig


tips = px.data.tips()

fig = barcode(tips, x="total_bill")
