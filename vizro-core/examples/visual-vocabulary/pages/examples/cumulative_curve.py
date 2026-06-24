import pandas as pd
import plotly.graph_objects as go
import vizro.plotly.express as px
from vizro.models.types import capture

tips = px.data.tips()


@capture("graph")
def cumulative_curve(data_frame: pd.DataFrame) -> go.Figure:
    fig = px.ecdf(data_frame, x="total_bill", markers=True)

    fig.update_traces(line={"width": 3})
    fig.update_yaxes(tickformat=".0%", title_text="Cumulative proportion")

    median = data_frame["total_bill"].median()
    q1 = data_frame["total_bill"].quantile(0.25)
    q3 = data_frame["total_bill"].quantile(0.75)

    for y, label, x_pos in [
        (0.5, f"Median (50th) = ${median:.1f}", median),
        (0.25, f"25th percentile = ${q1:.1f}", q1),
        (0.75, f"75th percentile = ${q3:.1f}", q3),
    ]:
        fig.add_hline(y=y, line_dash="dash", line_color="gray", opacity=0.25, line_width=1)
        fig.add_annotation(
            x=x_pos,
            y=y,
            text=label,
            arrowhead=1,
            arrowcolor="gray",
            ax=40,
            ay=-30,
            borderwidth=1,
        )

    return fig


fig = cumulative_curve(data_frame=tips)
