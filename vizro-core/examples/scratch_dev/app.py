"""Dev app to try things out."""

from datetime import date

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_data_table

iris = px.data.iris()


page = vm.Page(
    title="Container",
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
        vm.Table(figure=dash_data_table(iris)),
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

vm.Container.add_type("components", vm.Slider)

page_slider = vm.Page(
    title="Slider",
    components=[
        vm.Container(
            title="Slider examples",
            components=[
                vm.Slider(
                    title="Default slider",
                    min=0,
                    max=100,
                    step=20,
                ),
                vm.Slider(
                    title="Slider with tooltip",
                    min=0,
                    max=100,
                    step=20,
                    extra={"tooltip": {"placement": "bottom", "always_visible": True}},
                ),
            ],
        ),
    ],
)

vm.Container.add_type("components", vm.RangeSlider)

page_range_slider = vm.Page(
    title="Range Slider",
    components=[
        vm.Container(
            title="Range Slider examples",
            components=[
                vm.RangeSlider(
                    title="Default range slider",
                    min=0,
                    max=100,
                    step=20,
                ),
                vm.RangeSlider(
                    title="Range slider with marks",
                    min=0,
                    max=100,
                    step=20,
                    marks={0: "0%", 20: "20%", 40: "40%", 60: "60%", 80: "80%", 100: "100%"},
                    extra={
                        "tooltip": {"placement": "bottom", "always_visible": True},
                        "pushable": 20,
                    },
                ),
            ],
        ),
    ],
)

vm.Container.add_type("components", vm.DatePicker)

page_date_picker = vm.Page(
    title="Date Picker",
    components=[
        vm.Container(
            title="Date Picker examples",
            components=[
                vm.DatePicker(
                    title="Default date picker",
                    min=date(2024, 1, 1),
                    max=date(2024, 12, 31),
                ),
                vm.DatePicker(
                    title="Custom styled date picker",
                    min=date(2024, 1, 1),
                    max=date(2024, 12, 31),
                    range=False,
                    extra={
                        "size": "lg",
                        "valueFormat": "DD/MM/YYYY",
                        "placeholder": "Select a date",
                    },
                ),
                vm.DatePicker(
                    title="Range date picker with custom style",
                    min=date(2024, 1, 1),
                    max=date(2024, 12, 31),
                    range=True,
                    extra={
                        "size": "lg",
                        "valueFormat": "DD/MM/YYYY",
                        "placeholder": "Select date range",
                        "style": {"width": "300px"},
                        "dropdownType": "modal",
                    },
                ),
            ],
        ),
    ],
)

dashboard = vm.Dashboard(
    pages=[
        page,
        page_card,
        page_button,
        page_dropdown,
        page_checklist,
        page_radio,
        page_slider,
        page_range_slider,
        page_date_picker,
    ]
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
