"""Rough example used by developers."""

import dash_bootstrap_components as dbc
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models._components.form._text_area import TextArea
from vizro.models._components.form._user_input import UserInput

iris = px.data.iris()

# Only added to container.components directly for dev example
vm.Container.add_type("components", UserInput)
vm.Container.add_type("components", TextArea)

inputs = vm.Page(
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



graph = vm.Page(
    title="Graph",
    components=[
        vm.Graph(
            id="scatter_relation",
            figure=px.scatter(data_frame=px.data.gapminder(), x="gdpPercap", y="lifeExp", size="pop"),
        ),
    ],
    controls=[
        vm.Filter(
            column="continent",
            selector=vm.Dropdown(title="Dropdown Label"),
        ),
        vm.Filter(
            column="continent",
            selector=vm.Checklist(title="Checklist Label"),
        ),
        vm.Filter(
            column="year",
            selector=vm.RangeSlider(title="Range Slider Label"),
        ),
        vm.Filter(
            column="continent",
            selector=vm.RadioItems(title="Radio Items Label"),
        ),
        vm.Filter(
            column="year",
            selector=vm.Slider(title="Slider Label"),
        ),
    ]
)

dashboard = vm.Dashboard(pages=[inputs, graph])

if __name__ == "__main__":
    Vizro(external_stylesheets=[dbc.themes.BOOTSTRAP]).build(dashboard).run()
