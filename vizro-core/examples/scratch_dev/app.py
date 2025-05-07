"""Dev app to try things out."""

from vizro.tables import dash_ag_grid
from pydantic import AfterValidator, Field, PlainSerializer
from vizro.models.types import ActionType
from vizro.models._action._actions_chain import _action_validator_factory

from typing import Literal, Annotated

import dash_bootstrap_components as dbc
import vizro.models as vm
import vizro.plotly.express as px
from dash import html
from vizro import Vizro

from vizro.models.types import capture


df = px.data.iris()


# 1. Create new custom component
class OffCanvas(vm.VizroBaseModel):
    type: Literal["offcanvas"] = "offcanvas"
    title: str
    content: str

    def build(self):
        return html.Div(
            [
                dbc.Offcanvas(
                    children=html.P(self.content),
                    id=self.id,
                    title=self.title,
                    is_open=False,
                ),
            ]
        )


class Carousel(vm.VizroBaseModel):
    type: Literal["carousel"] = "carousel"
    items: list
    actions: Annotated[
        list[ActionType],
        # Here we set the action so a change in the active_index property of the custom component triggers the action
        AfterValidator(_action_validator_factory("active_index")),
        # Here we tell the serializer to only serialize the actions field
        PlainSerializer(lambda x: x[0].actions),
        Field(default=[]),
    ]

    def build(self):
        return dbc.Carousel(
            id=self.id,
            items=self.items,
        )


vm.Page.add_type("components", OffCanvas)
vm.Page.add_type("components", Carousel)


@capture("action")
def action_function(button_number_of_clicks):
    title = f"Button clicked {button_number_of_clicks} times."
    return title


@capture("action")
def action_function_dict(button_number_of_clicks):
    title = f"Button clicked {button_number_of_clicks} times."
    return {"anything": title}


@capture("action")
def action_function_multiple(button_number_of_clicks):
    title = f"Button clicked {button_number_of_clicks} times."
    is_open = True if button_number_of_clicks % 2 == 0 else False
    return title, is_open


@capture("action")
def action_function_multiple_dict(button_number_of_clicks):
    title = f"Button clicked {button_number_of_clicks} times."
    is_open = True if button_number_of_clicks % 2 == 0 else False
    return {"anything": title, "anything_two": is_open}


@capture("action")
def open_offcanvas(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


@capture("action")
def slide_next_card(active_index):
    if active_index:
        return "Second slide"

    return "First slide"


# Examples with list output  ----------
page_one = vm.Page(
    title="Page Smoke Title",
    components=[
        vm.Button(
            id="trigger-button",
            text="Click me",
            actions=[
                vm.Action(
                    function=action_function_multiple(),
                    inputs=["trigger-button.n_clicks"],
                    # This is how we had to define it before:
                    # outputs=["card-id.children"],
                    # Now we can just do this:
                    outputs=["card-id", "tooltip-id"],
                )
            ],
        ),
        vm.Card(
            id="card-id",
            text="Click the button to update me",
        ),
        vm.AgGrid(figure=dash_ag_grid(df)),
    ],
    controls=[
        vm.Filter(
            column="species",
            selector=vm.Dropdown(
                title="Species", description=vm.Tooltip(text="This is a tooltip", icon="info", id="tooltip-id")
            ),
        )
    ],
)

# Examples with dict output  ----------
page_one_b = vm.Page(
    title="Page Smoke Title B",
    components=[
        vm.Button(
            id="trigger-button-2",
            text="Click me",
            actions=[
                vm.Action(
                    function=action_function_multiple_dict(),
                    inputs=["trigger-button-2.n_clicks"],
                    outputs={"anything": "card-id-2", "anything_two": "tooltip-id-2"},
                )
            ],
        ),
        vm.Card(
            id="card-id-2",
            text="Click the button to update me",
        ),
        vm.AgGrid(figure=dash_ag_grid(df)),
    ],
    controls=[
        vm.Filter(
            column="species",
            selector=vm.Dropdown(
                title="Species", description=vm.Tooltip(text="This is a tooltip", icon="info", id="tooltip-id-2")
            ),
        )
    ],
)

# Examples in docs that should still work ----------
page_two = vm.Page(
    title="Custom Component A",
    components=[
        vm.Button(
            text="Open Offcanvas",
            id="open_button",
            actions=[
                vm.Action(
                    function=open_offcanvas(),
                    inputs=["open_button.n_clicks", "offcanvas.is_open"],
                    outputs=["offcanvas.is_open"],
                )
            ],
        ),
        OffCanvas(
            id="offcanvas",
            content="OffCanvas content",
            title="Offcanvas Title",
        ),
    ],
)


page_three = vm.Page(
    title="Custom Component B",
    components=[
        vm.Card(text="First slide", id="carousel-card"),
        Carousel(
            id="carousel",
            items=[
                {"key": "1", "src": "assets/placeholder.jpg"},
                {"key": "2", "src": "assets/placeholder.jpg"},
            ],
            actions=[
                vm.Action(
                    function=slide_next_card(),
                    # Custom components only work with model-id only if
                    # _input_default_property / output_default_property is defined
                    inputs=["carousel.active_index"],
                    # Previously:
                    # outputs=["carousel-card.children"],
                    # Now:
                    outputs=["carousel-card"],
                )
            ],
        ),
    ],
)


page_four = vm.Page(
    title="Check Validations",
    components=[
        vm.Button(
            id="button-id",
            actions=[
                vm.Action(
                    function=action_function(),  # or function=action_function_dict(),
                    inputs=["button-id"],
                    # Case A: Model-ID doesn't exist, syntax correct (only model-id)
                    # Throws KeyError before dashboard creation: "Component with ID 'wrong-id' not found.
                    # Please provide a valid component ID or use the explicit format '<component-id>.<property>'."
                    # outputs=["wrong-id"]
                    # outputs={"anything": "wrong-id"}
                    # Case B: Model-ID doesn't exist, syntax correct (dot notation), property can be anything
                    # Throws KeyError before dashboard creation: "Component with ID 'wrong-id' not found.
                    # Please provide a valid component ID or use the explicit format '<component-id>.<property>'."
                    # outputs=["wrong-id.prop"]
                    # outputs=["wrong-id.children"]
                    # outputs={"anything": "wrong-id.prop"}
                    # outputs={"anything": "wrong-id.children"}
                    # Case C: Model-ID exists but property doesn't exist
                    # Currently not captured at all - bad. Check how this worked before.
                    # outputs=["card-id-validation.prop"]
                    # outputs={"anything": "card-id-validation.prop"}
                    # Case D: Syntax - doesn't matter if model id/property exist or not
                    # Throws KeyError before dashboard creation: "Component with ID
                    # 'card-id-validation.children.children' not found. Please
                    # provide a valid component ID or use the explicit format '<component-id>.<property>'."
                    # outputs=["card-id-validation.children.children"]
                    # outputs=["card-id-validation..children.children"]
                    # outputs=["card-id..childre"]
                    # outputs={"anything": "card-id-validation..children"}
                )
            ],
        ),
        vm.Card(
            id="card-id-validation",
            text="Click the button to update me",
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page_one, page_two, page_three, page_four])

if __name__ == "__main__":
    Vizro().build(dashboard).run()

