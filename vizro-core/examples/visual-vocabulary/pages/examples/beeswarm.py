import pandas as pd
import plotly.graph_objects as go
import vizro.plotly.express as px
from vizro.models.types import capture

tips = px.data.tips()


@capture("graph")
def beeswarm(data_frame: pd.DataFrame, x: str, y: str, point_spacing: float = 0.12) -> go.Figure:
    def offset_candidates():
        yield 0.0
        level = 1

        while True:
            yield level * point_spacing
            yield -level * point_spacing
            level += 1

    def overlaps(candidate, value, placed):
        return any(
            abs(candidate - placed_offset) < point_spacing and abs(value - placed_value) < point_spacing
            for placed_offset, placed_value in placed
        )

    fig = go.Figure()

    categories = data_frame[x].unique()

    for category_index, category in enumerate(categories):
        category_data = data_frame[data_frame[x] == category].sort_values(y)
        placed = []

        x_positions = []
        y_positions = []

        for value in category_data[y]:
            for offset in offset_candidates():
                if not overlaps(offset, value, placed):
                    placed.append((offset, value))
                    x_positions.append(category_index + offset)
                    y_positions.append(value)
                    break

        fig.add_trace(
            go.Scatter(
                x=x_positions,
                y=y_positions,
                mode="markers",
                name=str(category),
            )
        )

        fig.update_xaxes(
            tickvals=list(range(len(categories))),
            ticktext=categories,
            title_text=x,
        )
    fig.update_yaxes(title_text=y)

    return fig


fig = beeswarm(tips, x="day", y="total_bill")
