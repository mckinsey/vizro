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


selectors = vm.Page(
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
            column="year",
            selector=vm.RangeSlider(title="Range Slider Label"),
        ),
        vm.Filter(
            column="year",
            selector=vm.Slider(title="Slider Label"),
        ),
        vm.Filter(
            column="year",
            selector=vm.RangeSlider(title="Range Slider Label", step=5),
        ),
        vm.Filter(
            column="year",
            selector=vm.Slider(title="Slider Label", step=5),
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

dashboard = vm.Dashboard(pages=[selectors])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
