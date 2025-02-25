"""Dev app to try things out."""

from os import chown

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture
from vizro.tables import dash_ag_grid

iris = px.data.iris()


@capture("ag_grid")
def my_custom_ag_grid(data_frame, chosen_columns, **kwargs):
    print(f"\nChosen column: {chosen_columns}\n")
    return dash_ag_grid(data_frame=data_frame[chosen_columns], **kwargs)()  # type: ignore


page = vm.Page(
    title="Page with subsections",
    layout=vm.Layout(grid=[[0, 3, 3, 3, 4, 4], [1, 3, 3, 3, 4, 4], [2, 3, 3, 3, 4, 4]]),
    components=[
        vm.Card(text="""Hello, this is a card with a [link](https://www.google.com)"""),  # type: ignore
        vm.Card(text="""Hello, this is a card with a [link](https://www.google.com)"""),  # type: ignore
        vm.Card(text="""Hello, this is a card with a [link](https://www.google.com)"""),  # type: ignore
        vm.Container(
            title="Container I",
            components=[
                vm.Graph(figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species")),  # type: ignore
            ],
            extra={"class_name": "bg-container", "fluid": False},
        ),
        vm.Container(
            title="Container II",
            components=[
                vm.Graph(figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species")),  # type: ignore
            ],
            extra={"class_name": "bg-container"},
        ),
    ],
)

page_two = vm.Page(
    title="Container",
    components=[
        vm.Container(
            title="Container III",
            components=[
                vm.Graph(figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species")),  # type: ignore
            ],
        ),
    ],
)

page_card = vm.Page(
    title="Card",
    components=[
        vm.Card(text="""First card"""),  # type: ignore
        vm.Card(text="""Second card""", extra={"class_name": "bg-success"}),  # type: ignore
    ],
)

page_button = vm.Page(
    title="Button",
    components=[
        vm.Button(text="Default button"),  # type: ignore
        vm.Button(text="Primary button", extra={"color": "primary"}),  # type: ignore
        vm.Button(text="Success button", extra={"color": "success", "outline": True}),  # type: ignore
    ],
)

vm.Container.add_type("components", vm.Dropdown)

page_dropdown = vm.Page(
    title="Dropdown",
    components=[
        vm.Container(
            title="Dropdown examples",
            components=[
                vm.Dropdown(
                    title="Default dropdown",
                    options=["Option 1", "Option 2", "Option 3"],
                ),
                vm.Dropdown(
                    title="Custom styled dropdown",
                    options=["Option 1", "Option 2", "Option 3"],
                    extra={"clearable": True, "placeholder": "Select an option...", "style": {"width": "300px"}},
                ),
                vm.Dropdown(
                    title="Single select dropdown",
                    options=["Option 1", "Option 2", "Option 3"],
                    multi=False,
                    extra={"style": {"backgroundColor": "#f8f9fa"}, "optionHeight": 200},
                ),
            ],
        ),
    ],
)

vm.Container.add_type("components", vm.Checklist)

page_checklist = vm.Page(
    title="Checklist",
    components=[
        vm.Container(
            title="Checklist examples",
            components=[
                vm.Checklist(
                    title="Default checklist",
                    options=["Option 1", "Option 2", "Option 3"],
                ),
                vm.Checklist(
                    title="Custom styled checklist",
                    options=["Option 1", "Option 2", "Option 3"],
                    extra={"switch": True, "inline": True},
                ),
                vm.Checklist(
                    title="Colored checklist",
                    options=["Option 1", "Option 2", "Option 3"],
                    extra={
                        "input_checked_style": {"backgroundColor": "#198754"},
                        "input_style": {"borderColor": "#198754"},
                    },
                ),
            ],
        ),
    ],
)

vm.Container.add_type("components", vm.RadioItems)

page_radio = vm.Page(
    title="Radio Items",
    components=[
        vm.Container(
            title="Radio Items examples",
            components=[
                vm.RadioItems(
                    title="Default radio items",
                    options=["Option 1", "Option 2", "Option 3"],
                ),
                vm.RadioItems(
                    title="Inline radio items",
                    options=["Option 1", "Option 2", "Option 3"],
                    extra={"inline": True},
                ),
                vm.RadioItems(
                    title="Custom styled radio items",
                    options=["Option 1", "Option 2", "Option 3"],
                    extra={
                        "input_checked_style": {"backgroundColor": "#198754"},
                        "input_style": {"borderColor": "#198754"},
                    },
                ),
            ],
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page, page_two, page_card, page_button, page_dropdown, page_checklist, page_radio])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
