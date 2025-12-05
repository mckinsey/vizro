import vizro.models as vm
import vizro.plotly.express as px
from vizro.managers import data_manager
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
        color_continuous_scale=["#0a0814", "#1a1442", "#2d2463"],
    )


# Page definition
page = vm.Page(
    title="Correlation matrix",
    components=[vm.Graph(figure=correlation_heatmap(data_frame="iris"))],
)
