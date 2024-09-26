from typing import List

import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm
from vizro import Vizro
from vizro.models.types import capture

sankey_data = pd.DataFrame(
    {
        "Origin": [0, 1, 0, 2, 3, 3],  # indices inside labels
        "Destination": [2, 3, 3, 4, 4, 5],  # indices inside labels
        "Value": [8, 4, 2, 8, 4, 2],
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
                node={
                    "pad": 16,
                    "thickness": 16,
                    "label": labels,
                },
                link={
                    "source": data_frame[source],
                    "target": data_frame[target],
                    "value": data_frame[value],
                    "label": labels,
                    "color": "rgba(205, 209, 228, 0.4)",
                },
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
                labels=["A1", "A2", "B1", "B2", "C1", "C2"],
                source="Origin",
                target="Destination",
                value="Value",
            ),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
