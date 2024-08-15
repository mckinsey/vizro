"""asdf."""
import plotly.graph_objs as go
import plotly.io as pio
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture

# This is applied properly as the final title color is taken from the fig.layout.template
# (which is calculated from the current pio.template)
pio.templates["vizro_dark"]["layout"]["title"]["font"]["color"] = "green"
pio.templates["vizro_light"]["layout"]["title"]["font"]["color"] = "blue"

# This doesn't work as expected as the final scatter points color is taken from fig.data
# (which is calculated probably from the pio.templates.default)
pio.templates["vizro_dark"]["layout"]["colorway"] = ["red"]
pio.templates["vizro_light"]["layout"]["colorway"] = ["yellow"]

df = px.data.iris()


@capture("graph")
def my_graph_figure_px(data_frame):
    """Blah."""
    fig = px.scatter(data_frame, x="sepal_width", y="sepal_length", title="Title")
    return fig


@capture("graph")
def my_graph_figure_go(data_frame):
    """Blahhrl."""
    fig = go.Figure(go.Scatter(x=data_frame["sepal_width"], y=data_frame["sepal_length"]))
    fig.update_layout(title="Title")
    return fig


page = vm.Page(
    title="Test",
    components=[
        vm.Graph(figure=px.scatter(df, x="sepal_width", y="sepal_length", title="Title")),
        vm.Graph(figure=my_graph_figure_px(df)),
        vm.Graph(figure=my_graph_figure_go(df)),
    ],
    controls=[vm.Filter(column="species")],
)

# Try with theme="vizro_light"
dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
