"""Dev app to try things out."""

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture

animals = pd.DataFrame(
    {"animals": ["giraffes", "orangutans", "monkeys"], "value": [20, 14, 23], "color": ["Male", "Female", "Female"]}
)

iris = px.data.iris()


@capture("graph")
def bar(data_frame):
    """LA LA LA LA."""
    fig = px.bar(data_frame, x="sepal_length", y="sepal_width", color="species")
    return fig


@capture("graph")
def px_bar(data_frame):
    """LA LA LA LA."""
    fig = px.bar(data_frame, x="animals", y="value", color="color")
    return fig


page = vm.Page(
    title="My first page",
    components=[
        vm.Graph(figure=bar(iris)),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
