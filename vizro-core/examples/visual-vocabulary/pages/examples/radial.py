import pandas as pd
import vizro.plotly.express as px
from vizro.models.types import capture


@capture("graph")
def radial(data_frame: pd.DataFrame, **kwargs):
    """Creates a radial chart using Plotly."""
    fig = px.bar_polar(data_frame, **kwargs)
    fig.update_layout(
        legend_title_text="Wind speed",
        polar={
            "angularaxis": {"direction": "clockwise", "rotation": 90},
            "radialaxis": {"ticksuffix": "%"},
        },
    )
    return fig


wind = px.data.wind()

fig = radial(
    wind,
    r="frequency",
    theta="direction",
    color="strength",
    labels={"direction": "Direction", "frequency": "Frequency", "strength": "Wind speed"},
)
