
from vizro import Vizro

from typing import Literal
import dash_mantine_components as dmc
import vizro.models as vm
from dash import html

class StepperTimeline(vm.VizroBaseModel):
    type: Literal["stepper_timeline"] = "stepper_timeline"
    items: list  # List of dicts, each representing a step
    # active: int = 0  # Always set to -1 in build

    def build(self):
        return html.Div(
            dmc.Stepper(
                active=-1,  # No step is active
                orientation="horizontal",
                allowNextStepsSelect=False,
                children=[
                    dmc.StepperStep(
                        label=item.get("title", ""),
                        description=item.get("content", ""),
                        icon=item.get("icon")
                    )
                    for item in self.items
                ],
                style={"width": "100%"}
            ),
            style={"display": "flex", "alignItems": "center", "height": "100%", "width": "100%"}
        )

# Register the StepperTimeline component
vm.Page.add_type("components", StepperTimeline)
vm.Container.add_type("components", StepperTimeline)

# Use the Material Symbols Outlined 'description' icon
icon_url = "assets/icons/description.svg#icon-left"
card_text = f"""

### Page Title
This card provides a summary or entry point for the corresponding page.
"""

context_card_text = f"""

### Context
View context about the case study.
"""

card_style = {"height": "180px", "width": "340px"}
context_page_card_style = {"height": "280px", "width": "260px"}

context_md = """
### Context
A large bank has customer data stored on multiple systems and suspects some DQ issues to be present.

**They already use Collibra** as a data management tool but currently don't possess the capabilities to solve several slightly more nuanced DQ challenges.

Both sales and finance departments have customer datasets which contain:

1. Personal customer information e.g., Address, email etc.
2. Transaction information e.g., Number of annual transactions per customer; customer type (bronze, silver, gold etc.)
"""

dq_problems_md = """
### Data quality problems
1. The organisation wants to check whether all individuals have been **correctly classified (customer type)** and **transaction amounts** based on their transaction history

2. Both Finance and Sales departments have their own version of the customer data, which are expected to **contain conflicting information**, and do not have an **enterprise global level ID**
"""

# stepper_items = [
#     {"title": html.A("Summary", href="/summary"), "content": "Diagnostic Summary", "icon": html.Img(src="assets/icons/cube.svg", width=24, height=24, style={"filter": "invert(66%) sepia(97%) saturate(749%) hue-rotate(181deg) brightness(102%) contrast(101%)"})},  # match blue
#     {"title": "Detect", "content": "Detect DQ issues", "icon": html.Img(src="assets/icons/cube.svg", width=24, height=24, style={"filter": "invert(62%) sepia(94%) saturate(355%) hue-rotate(120deg) brightness(92%) contrast(92%)"})},  # turquoise
#     {"title": "Correct", "content": "Correct DQ issues", "icon": html.Img(src="assets/icons/cube.svg", width=24, height=24, style={"filter": "invert(62%) sepia(94%) saturate(355%) hue-rotate(120deg) brightness(92%) contrast(92%)"})},  # turquoise
#     {"title": "Monitor", "content": "Monitor DQ issues", "icon": html.Img(src="assets/icons/cube.svg", width=24, height=24, style={"filter": "invert(36%) sepia(98%) saturate(7492%) hue-rotate(288deg) brightness(95%) contrast(101%)"})},  # vibrant pink
# ]

# stepper_component = StepperTimeline(
#     items=stepper_items
# )

model = vm.Dashboard(
    pages=[
        vm.Page(
            components=[
                vm.Container(
                    id="container1",
                    title="I gave this title",
                    # type="container",
                    # collapsed=True,
                    variant="outlined",
                    # layout=vm.Flex(direction="column", gap="20px", wrap=False),
                    components=[
                        vm.Container(
                            id="container2",
                            # type="container",
                            layout=vm.Flex(direction="row", gap="20px", wrap=True),
                            components=[
                                vm.Card(type="card", text=context_card_text, extra={"style": card_style}, href="/context",),
                                vm.Card(type="card", text=card_text, extra={"style": card_style}),
                                vm.Card(type="card", text=card_text, extra={"style": card_style}),
                                vm.Card(type="card", text=card_text, extra={"style": card_style})
                            ],
                            title="Overview",
                            variant="filled",
                            collapsed=False,
                        ),
                        vm.Container(
                            id="container3",
                            # type="container",
                            layout=vm.Flex(direction="row", gap="20px", wrap=True),
                            components=[
                                vm.Card(type="card", text=card_text, extra={"style": card_style}),
                                vm.Card(type="card", text=card_text, extra={"style": card_style}),
                                vm.Card(type="card", text=card_text, extra={"style": card_style}),
                                vm.Card(type="card", text=card_text, extra={"style": card_style}),
                            ],
                            title="Detect",
                            variant="filled",
                            collapsed=False,
                        ),
                        vm.Container(
                            id="container4",
                            variant="filled",
                            # type="container",
                            layout=vm.Flex(direction="row", gap="20px", wrap=True),
                            components=[
                                vm.Card(type="card", text=card_text, extra={"style": card_style}),
                                vm.Card(type="card", text=card_text, extra={"style": card_style}),
                                vm.Card(type="card", text=card_text, extra={"style": card_style}),
                                vm.Card(type="card", text=card_text, extra={"style": card_style})
                            ],
                            title="Correct",
                            collapsed=False,
                        ),
                        vm.Container(
                            id="container5",
                            variant="filled",
                            # type="container",
                            layout=vm.Flex(direction="row", gap="20px", wrap=True),
                            components=[
                                vm.Card(type="card", text=card_text, extra={"style": card_style}),
                                vm.Card(type="card", text=card_text, extra={"style": card_style}),
                                vm.Card(type="card", text=card_text, extra={"style": card_style}),
                                vm.Card(type="card", text=card_text, extra={"style": card_style})
                            ],
                            title="Monitor",
                            # collapsed=False,
                        ),
                    ],
                ),
                # vm.Container(
                #     title="Added container",
                #     collapsed=False,
                #     variant="outlined",
                #     components=[
                #         vm.Card(text="test"),
                #     ]
                # )
            ],
            title="Menu",
        ),
        vm.Page(
            components=[
                vm.Container(
                    id="container6",
                    title="I gave this title as well",
                    # type="container",
                    # collapsed=False,
                    layout=vm.Grid(grid=[[0, 1],[0, 1]]),
                    components=[
                        vm.Card(type="card", text="test", extra={"style": {"height": "100%", "width": "100%"}}),
                        vm.Card(type="card", text="test", extra={"style": {"height": "100%", "width": "100%"}}),
                    ],
                )
            ],
            title="Context",
        )
    ],
    theme="vizro_dark",
    title="",
)

Vizro().build(model).run()
