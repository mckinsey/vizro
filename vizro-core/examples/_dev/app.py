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
            layout=vm.Layout(grid=[[i] for i in range(8)], row_min_height="72px"),
            components=[
                UserInput(title="Input - Text (single-line)", placeholder="Enter text here", input_type="text"),
                UserInput(title="Input - Number", placeholder="Enter a number here", input_type="number"),
                UserInput(title="Input - Password", placeholder="Enter a password here", input_type="password"),
                UserInput(title="Input - Email", placeholder="Enter an email here", input_type="email"),
                UserInput(title="Input - Search", placeholder="Enter a search here", input_type="search"),
                UserInput(title="Input - Tel", placeholder="Enter a phone number here", input_type="tel"),
                UserInput(title="Input - URL", placeholder="Enter a url here", input_type="url"),
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
