"""Rough example used by developers."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models._components.form._text_area import TextArea
from vizro.models._components.form._user_input import UserInput

iris = px.data.iris()

# Only added to container.components directly for dev example
vm.Container.add_type("components", UserInput)
vm.Container.add_type("components", TextArea)

page = vm.Page(
    title="User Text Inputs",
    layout=vm.Layout(grid=[[0, 1]], col_gap="40px"),
    components=[
        vm.Container(
            title="Input Components",
            components=[
                UserInput(title="Input - Text (single-line)", placeholder="Enter text here"),
                TextArea(title="Input - Text (multi-line)", placeholder="Enter multi-line text here"),
            ],
        ),
        vm.Graph(
            id="for_custom_chart",
            figure=px.scatter(iris, title="Iris Dataset", x="sepal_length", y="petal_width", color="sepal_width"),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
