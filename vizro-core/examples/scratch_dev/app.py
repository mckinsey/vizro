"""Test app"""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

page = vm.Page(
    title="foo", components=[vm.Graph(figure=px.scatter(data_frame=px.data.iris(), x="sepal_width", y="sepal_length"))]
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
