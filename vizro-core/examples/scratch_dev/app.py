"""Test app"""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
import plotly.io as pio

# TODO: Move somewhere else, just for testing
pio.templates["vizro_dark"].layout.paper_bgcolor = "rgba(0, 0, 0, 0)"
pio.templates["vizro_light"].layout.paper_bgcolor = "rgba(0, 0, 0, 0)"
pio.templates["vizro_dark"].layout.plot_bgcolor = "rgba(0, 0, 0, 0)"
pio.templates["vizro_light"].layout.plot_bgcolor = "rgba(0, 0, 0, 0)"

page = vm.Page(
    title="foo",
    layout=vm.Layout(grid=[[0, 1]]),
    components=[

        vm.Container(title="Container I",
                     components=[vm.Graph(figure=px.scatter(data_frame=px.data.iris(), x="sepal_width", y="sepal_length"))],
                     classname="container-fluid border"),
        vm.Container(title="Container II",
                     components=[
                         vm.Graph(figure=px.scatter(data_frame=px.data.iris(), x="sepal_width", y="sepal_length"))],
                     classname="container-fluid bg-container"),
    ]
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
