from typing import List

import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm
from vizro import Vizro
from vizro.models.types import capture

waterfall_data = pd.DataFrame(
    {
        "x": ["Sales", "Consulting", "Net revenue", "Purchases", "Other expenses", "Profit before tax"],
        "y": [60, 80, 0, -40, -20, 0],
        "measure": ["relative", "relative", "total", "relative", "relative", "total"],
    }
)


@capture("graph")
def waterfall(
    data_frame: pd.DataFrame,
    x: str,
    y: str,
    measure: List[str],
):
    fig = go.Figure(
        go.Waterfall(
            x=data_frame[x],
            y=data_frame[y],
            measure=data_frame[measure],
        )
    )
    fig.update_layout(showlegend=False)
    return fig


page = vm.Page(
    title="Waterfall",
    components=[
        vm.Graph(
            figure=waterfall(
                waterfall_data,
                x="x",
                y="y",
                measure="measure",
            )
        )
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
