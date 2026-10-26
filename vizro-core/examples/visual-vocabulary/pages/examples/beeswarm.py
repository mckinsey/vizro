import pandas as pd
import plotly.graph_objects as go
import vizro.plotly.express as px
from vizro.models.types import capture

iris = px.data.iris()


@capture("graph")
def beeswarm(
    data_frame: pd.DataFrame,
    x: str,
    y: str,
    point_spacing: float = 0.05,
    y_tolerance_fraction: float = 0.02,
) -> go.Figure:
    y_range = data_frame[y].max() - data_frame[y].min()
    y_tolerance = max(y_range * y_tolerance_fraction, 1e-9)
    max_offset = 0.5 - point_spacing

    def offset_candidates():
        yield 0.0
        level = 1

        while level * point_spacing <= max_offset:
            yield level * point_spacing
            yield -level * point_spacing
            level += 1

    def overlaps(candidate, value, placed):
        return any(
            abs(candidate - placed_offset) < point_spacing and abs(value - placed_value) < y_tolerance
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
            else:
                offset = max_offset if len(placed) % 2 == 0 else -max_offset
                placed.append((offset, value))
                x_positions.append(category_index + offset)
                y_positions.append(value)

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


fig = beeswarm(iris, x="species", y="petal_length")
