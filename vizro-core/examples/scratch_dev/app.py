from typing import Annotated, Literal

import dash_bootstrap_components as dbc
import vizro.models as vm
from pydantic import AfterValidator, Field, PlainSerializer
from vizro import Vizro
from vizro.models import Action
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models.types import capture


# 1. Create new custom component
class Carousel(vm.VizroBaseModel):
    type: Literal["carousel"] = "carousel"
    items: list
    actions: Annotated[
        list[Action],
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


# 2. Add new components to expected type - here the selector of the parent components
vm.Page.add_type("components", Carousel)


# 3. Create custom action
@capture("action")
def slide_next_card(active_index):
    if active_index:
        return "Second slide"

    return "First slide"


page = vm.Page(
    title="Custom Component",
    components=[
        vm.Card(text="First slide", id="carousel-card"),
        Carousel(
            id="carousel",
            items=[
                {"key": "1", "src": "assets/slide_1.jpg"},
                {"key": "2", "src": "assets/slide_2.jpg"},
            ],
            actions=[
                vm.Action(
                    function=slide_next_card(),
                    inputs=["carousel.active_index"],
                    outputs=["carousel-card.children"],
                )
            ],
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

Vizro().build(dashboard).run()
