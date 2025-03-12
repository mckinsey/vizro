import pandas as pd
import plotly.graph_objects as go
from vizro.models.types import capture


@capture("graph")
def sankey(
    data_frame: pd.DataFrame,
    source: str,
    target: str,
    value: str,
    labels: list[str],
):
    return go.Figure(
        data=go.Sankey(
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
        ),
        layout={"barmode": "relative"},
    )


sankey_data = pd.DataFrame(
    {
        "Origin": [0, 1, 0, 2, 3, 3],  # indices inside labels
        "Destination": [2, 3, 3, 4, 4, 5],  # indices inside labels
        "Value": [8, 4, 2, 8, 4, 2],
    }
)

fig = sankey(
    sankey_data, labels=["A1", "A2", "B1", "B2", "C1", "C2"], source="Origin", target="Destination", value="Value"
)
