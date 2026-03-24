"""Custom charts for the app."""

import vizro.plotly.express as px
from vizro.models.types import capture


@capture("graph")
def bump_chart_with_highlight(data_frame, highlight_countries=None):
    """Custom bump chart based on px."""
    rank = data_frame.groupby("year")["lifeExp"].rank(method="dense", ascending=False)

    fig = px.line(data_frame, x="year", y=rank, color="country", markers=True)
    fig.update_yaxes(title="Rank (1 = Highest lifeExp)", autorange="reversed", dtick=1)
    fig.update_traces(opacity=0.3, line_width=2)

    if highlight_countries:
        for country in highlight_countries:
            fig.update_traces(selector={"name": country}, opacity=1, line_width=3)

    return fig
