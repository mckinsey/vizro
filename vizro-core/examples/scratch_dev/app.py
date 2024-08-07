import plotly.graph_objs as go
import plotly.io as pio
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture

pio.templates["vizro_dark"]["layout"]["colorway"] = ["red"]
pio.templates["vizro_light"]["layout"]["colorway"] = ["yellow"]

df = px.data.iris()


@capture("graph")
def my_graph_figure_px(data_frame):
    """Blah"""
    return px.scatter(data_frame, x="sepal_width", y="sepal_length")


@capture("graph")
def my_graph_figure_go(data_frame):
    """Blahhrl"""
    return go.Figure(go.Scatter(x=data_frame["sepal_width"], y=data_frame["sepal_length"]))


page = vm.Page(
    title="Test",
    components=[
        vm.Graph(figure=px.scatter(df, x="sepal_width", y="sepal_length")),
        vm.Graph(figure=my_graph_figure_px(df)),
        vm.Graph(figure=my_graph_figure_go(df)),
    ],
    controls=[vm.Filter(column="species")],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
