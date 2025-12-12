import vizro.plotly.express as px
from vizro.models.types import capture

iris = px.data.iris().select_dtypes("number")

@capture("graph")
def correlation_heatmap(data_frame):
    return px.imshow(
        data_frame.corr(),
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu",
        zmin=-1,
        zmax=1,
    )


fig = correlation_heatmap(data_frame=iris)
