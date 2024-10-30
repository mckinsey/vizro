import pandas as pd
import vizro.plotly.express as px
from vizro.models.types import capture


@capture("graph")
def radar(data_frame: pd.DataFrame, **kwargs):
    fig = px.line_polar(data_frame, **kwargs)
    fig.update_traces(fill="toself")
    return fig


wind = px.data.wind().query("strength == '1-2'")

fig = radar(wind, r="frequency", theta="direction", line_close=True)
