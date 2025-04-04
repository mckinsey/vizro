"""Example app from the official vizro user tutorial.

See: https://vizro.readthedocs.io/en/stable/pages/tutorials/explore-components/
"""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

iris = px.data.iris()

page = vm.Page(
    title="Collapsible containers",
    layout=vm.Layout(grid=[[0, 1]]),
    components=[
        vm.Container(
            title="Initially collapsed container",
            components=[vm.Graph(figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species"))],
            collapsed=True,
            variant="filled",
        ),
        vm.Container(
            title="Initially expanded container",
            components=[vm.Graph(figure=px.box(iris, x="species", y="sepal_length", color="species"))],
            collapsed=False,
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
