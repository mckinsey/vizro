"""Dev app to try things out."""

import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture

animals = pd.DataFrame(
    {"animals": ["giraffes", "orangutans", "monkeys"], "value": [20, 14, 23], "color": ["Male", "Female", "Female"]}
)


@capture("graph")
def bar(data_frame):
    """LA LA LA LA."""
    df_one = data_frame.query("color=='Male'")
    df_two = data_frame.query("color=='Female'")

    fig = go.Figure(
        data=[
            go.Bar(x=df_one["animals"], y=df_one["value"], name="High", marker_color="#00b4ff"),
        ],
    )

    fig.add_trace(go.Bar(x=df_two["animals"], y=df_two["value"], name="Low", marker_color="#ff9222"))
    return fig


@capture("graph")
def px_bar(data_frame):
    """LA LA LA LA."""
    fig = px.bar(data_frame, x="animals", y="value", color="color")
    return fig


page = vm.Page(
    title="My first page",
    components=[
        vm.Graph(figure=bar(animals)),
        vm.Graph(figure=px_bar(animals)),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
