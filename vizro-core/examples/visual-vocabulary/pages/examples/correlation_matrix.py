import vizro.models as vm
import vizro.plotly.express as px
from vizro.models.types import capture

# Note iris data
iris = px.data.iris().select_dtypes("number")


# Chart definition
@capture("graph")
def correlation_heatmap(data_frame):
    return px.imshow(
        data_frame.corr(),
        text_auto=True,
        aspect="auto",
    )


# Page definition
page = vm.Page(
    title="Correlation matrix",
    components=[vm.Graph(figure=correlation_heatmap(data_frame="iris"))],
)
