"""Scratch dev app."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro


df = px.data.iris()


page = vm.Page(
    title="Chart without ModeBar",
    components=[
        vm.Graph(
            figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"),
            extra={"config": {"displayModeBar": False}},
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=False)
