"""Rough example used by developers."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models._components.form._text_area import TextArea
from vizro.models._components.form._user_input import UserInput

iris = px.data.iris()

# Only added to container.components directly for dev example
vm.Page.add_type("controls", UserInput)
vm.Page.add_type("controls", TextArea)
vm.Container.add_type("components", vm.Dropdown)
vm.Container.add_type("components", vm.Checklist)
vm.Container.add_type("components", vm.RadioItems)
vm.Container.add_type("components", vm.Slider)
vm.Container.add_type("components", vm.RangeSlider)
vm.Container.add_type("components", TextArea)
vm.Container.add_type("components", UserInput)


selectors = vm.Page(
    title="Selectors - Controls",
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
            column="year",
            selector=vm.RangeSlider(title="Range Slider Label", step=1, marks=None),
        ),
        vm.Filter(
            column="year",
            selector=vm.Slider(title="Slider Label"),
        ),
        vm.Filter(
            column="year",
            selector=vm.RangeSlider(title="Range Slider Label", step=10),
        ),
        vm.Filter(
            column="year",
            selector=vm.Slider(title="Slider Label", step=10),
        ),
        vm.Filter(
            column="continent",
            selector=vm.Checklist(title="Checklist Label"),
        ),
        vm.Filter(
            column="continent",
            selector=vm.RadioItems(title="Radio Items Label"),
        ),
        UserInput(title="Input - Text (single-line)", placeholder="Enter text here"),
        TextArea(title="Input - Text (multi-line)", placeholder="Enter multi-line text here"),
    ],
)

form_components = vm.Page(
    title="Selectors - Components",
    components=[
        vm.Container(
            id="container-id",
            title="Form",
            components=[
                UserInput(title="Input - Text (single-line)", placeholder="Enter text here"),
                TextArea(title="Input - Text (multi-line)", placeholder="Enter multi-line text here"),
                vm.Dropdown(title="Dropdown - Single", options=["Option 1", "Option 2", "Option 3"], multi=False),
                vm.Dropdown(title="Dropdown - Multi", options=["Option 1", "Option 2", "Option 3"], multi=True),
                vm.Checklist(title="Checklist", options=["Option 1", "Option 2", "Option 3"]),
                vm.RadioItems(title="Radio Items", options=["Option 1", "Option 2", "Option 3"]),
                vm.Slider(title="Slider without marks", min=0, max=10),
                vm.Slider(title="Slider with marks", min=0, max=10, step=1),
                vm.RangeSlider(title="Range Slider without marks", min=0, max=10),
                vm.RangeSlider(title="Range Slider with marks", min=0, max=10, step=1),
                vm.Button(),
            ],
        ),
    ],
)


slider_marks = vm.Page(
    title="Sliders - drawn marks",
    layout=vm.Layout(grid=[[0, 1]], col_gap="100px"),
    components=[
        vm.Container(
            id="container-id-2",
            title="Range Slider",
            components=[
                vm.RangeSlider(title="Range Slider | step = None and marks = {}", min=0, max=10),
                vm.RangeSlider(
                    title="Range Slider | step = None and marks = {''}",
                    min=0,
                    max=10,
                    step=None,
                    marks={0: "0", 5: "5", 10: "10"},
                ),
                vm.RangeSlider(
                    title="Range Slider | step = None and marks = None", min=0, max=10, step=None, marks=None
                ),
                vm.RangeSlider(title="Range Slider | step = 1 and marks = {}", min=0, max=10, step=1),
                vm.RangeSlider(
                    title="Range Slider | step = 1 and marks = {''}",
                    min=0,
                    max=10,
                    step=1,
                    marks={0: "0", 5: "5", 10: "10"},
                ),
                vm.RangeSlider(title="Range Slider | step = 1 and marks = None", min=0, max=10, step=1, marks=None),
            ],
        ),
        vm.Container(
            id="container-id-3",
            title="Slider",
            components=[
                vm.Slider(title="Slider | step = None and marks = {}", min=0, max=10),
                vm.Slider(
                    title="Slider | step = None and marks = {''}",
                    min=0,
                    max=10,
                    step=None,
                    marks={0: "0", 5: "5", 10: "10"},
                ),
                vm.Slider(
                    title="Slider | step = None and marks = None", min=0, max=10, step=None, marks=None
                ),
                vm.Slider(title="Slider | step = 1 and marks = {}", min=0, max=10, step=1),
                vm.Slider(
                    title="Slider | step = 1 and marks = {''}",
                    min=0,
                    max=10,
                    step=1,
                    marks={0: "0", 5: "5", 10: "10"},
                ),
                vm.Slider(title="Slider | step = 1 and marks = None", min=0, max=10, step=1, marks=None),
            ],
        ),
    ],
)

dashboard = vm.Dashboard(pages=[selectors, form_components, slider_marks])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
