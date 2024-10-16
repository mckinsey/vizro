import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm
from vizro import Vizro
from vizro.models.types import capture

# Create the pastry data
pastries = pd.DataFrame(
    {
        "pastry": [
            "Scones",
            "Bagels",
            "Muffins",
            "Cakes",
            "Donuts",
            "Cookies",
            "Croissants",
            "Eclairs",
            "Brownies",
            "Tarts",
            "Macarons",
            "Pies",
        ],
        "Profit Ratio": [-0.10, -0.15, -0.05, 0.10, 0.05, 0.20, 0.15, -0.08, 0.08, -0.12, 0.02, -0.07],
        "Strongly Disagree": [20, 30, 10, 5, 15, 5, 10, 25, 8, 20, 5, 10],
        "Disagree": [30, 25, 20, 10, 20, 10, 15, 30, 12, 30, 10, 15],
        "Agree": [30, 25, 40, 40, 45, 40, 40, 25, 40, 30, 45, 35],
        "Strongly Agree": [20, 20, 30, 45, 20, 45, 35, 20, 40, 20, 40, 40],
    }
)


@capture("graph")
def diverging_stacked_bar(data_frame):
    fig = go.Figure()

    # Add traces for negative side
    for col in data_frame.columns[2:4]:
        fig.add_trace(
            go.Bar(
                x=-data_frame[col].values,
                y=data_frame["pastry"],
                orientation="h",
                name=col,
                customdata=data_frame[col],
            )
        )

    # Add traces for positive side
    for col in data_frame.columns[4:]:
        fig.add_trace(
            go.Bar(
                x=data_frame[col],
                y=data_frame["pastry"],
                orientation="h",
                name=col,
            )
        )

    # Update layout and add vertical line
    fig.update_layout(barmode="relative")
    fig.add_vline(x=0, line_width=2, line_color="grey")
    return fig


page = vm.Page(
    title="Diverging stacked bar",
    components=[
        vm.Graph(
            figure=diverging_stacked_bar(data_frame=pastries),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
