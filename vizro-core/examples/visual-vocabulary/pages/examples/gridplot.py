import plotly.graph_objects as go
import vizro.plotly.express as px
from plotly.subplots import make_subplots
from vizro.models.types import capture
from vizro.themes._palettes import qualitative

tips = px.data.tips()

day_order = ["Thur", "Fri", "Sat", "Sun"]
day_colors = dict(zip(day_order, qualitative[:4]))


@capture("graph")
def gridplot(data_frame):
    fig = make_subplots(
        rows=2,
        cols=2,
        column_titles=["Male", "Female"],
        row_titles=["Lunch", "Dinner"],
        specs=[[{"type": "pie"}, {"type": "pie"}], [{"type": "pie"}, {"type": "pie"}]],
        vertical_spacing=0.12,
    )

    subsets = [
        ("Lunch", "Male", 1, 1),
        ("Lunch", "Female", 1, 2),
        ("Dinner", "Male", 2, 1),
        ("Dinner", "Female", 2, 2),
    ]

    for time_val, sex_val, row, col in subsets:
        subset = data_frame[(data_frame["time"] == time_val) & (data_frame["sex"] == sex_val)]
        day_counts = subset["day"].value_counts()

        labels = [day for day in day_order if day in day_counts.index]
        values = [day_counts[day] for day in labels]
        colors = [day_colors[day] for day in labels]

        fig.add_trace(
            go.Pie(
                labels=labels,
                values=values,
                showlegend=False,
                hole=0.25,
                textposition="inside",
                marker={"colors": colors},
                sort=False,
            ),
            row=row,
            col=col,
        )

    for day in day_order:
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                marker={"size": 10, "color": day_colors[day]},
                name=day,
                hoverinfo="none",
            )
        )

    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(
        legend={"orientation": "h", "yanchor": "top", "y": -0.1, "xanchor": "center", "x": 0.5},
    )
    return fig


fig = gridplot(data_frame=tips)
