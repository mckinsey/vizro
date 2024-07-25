import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm
from vizro import Vizro
from vizro.models.types import capture
from typing import List

sankey_data = pd.DataFrame(
    {
        "Origin": [0, 1, 2, 1, 2, 4, 0],  # indices inside labels
        "Destination": [1, 2, 3, 4, 5, 5, 6],  # indices inside labels
        "Value": [10, 4, 8, 6, 4, 8, 8],
    }
)


@capture("graph")
def sankey(
    data_frame: pd.DataFrame,
    source: str,
    target: str,
    value: str,
    labels: List[str],
):
    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=16,
                    thickness=16,
                    label=labels,
                ),
                link=dict(
                    source=data_frame[source],
                    target=data_frame[target],
                    value=data_frame[value],
                    label=labels,
                    color="rgba(205, 209, 228, 0.4)",
                ),
            )
        ]
    )
    fig.update_layout(barmode="relative")
    return fig


page = vm.Page(
    title="Sankey",
    components=[
        vm.Graph(
            figure=sankey(
                sankey_data,
                labels=["A1", "A2", "B1", "B2", "C1", "C2", "D1"],
                source="Origin",
                target="Destination",
                value="Value",
            ),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
