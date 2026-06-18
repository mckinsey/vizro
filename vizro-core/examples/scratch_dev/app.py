"""Scratch demo app.

Run with debug=True to see the Vizro action logs panel in the Dash debug menu.
"""

import vizro.models as vm
import vizro.plotly.express as px

from vizro import Vizro

iris = px.data.iris()


page_action_logs = vm.Page(
    title="Action Logs Demo",
    components=[
        vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
    ],
    controls=[
        vm.Filter(column="species"),
    ],
)

dashboard = vm.Dashboard(
    pages=[
        page_action_logs,
    ],
)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=False)
