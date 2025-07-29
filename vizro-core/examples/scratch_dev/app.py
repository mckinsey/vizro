from typing import Annotated, Literal

import dash_bootstrap_components as dbc
import vizro.models as vm
from pydantic import model_validator
from vizro import Vizro
from vizro.models._models_utils import make_actions_chain
from vizro.models.types import ActionType
from vizro.models.types import capture


class Carousel(vm.VizroBaseModel):  # (1)!
    type: Literal["carousel"] = "carousel"
    items: list
    actions: list[ActionType] = []

    _make_actions_chain = model_validator(mode="after")(make_actions_chain)

    @property
    def _action_triggers(self):
        return {"__default__": f"{self.id}.active_index"}  # (2)!

    def build(self):
        return dbc.Carousel(id=self.id, items=self.items)


vm.Page.add_type("components", Carousel)  # (3)!


@capture("action")  # (4)!
def slide_next_card(active_index):
    if active_index:
        return "Second slide"
    return "First slide"


page = vm.Page(
    title="Custom Component",
    components=[
        vm.Card(text="First slide", id="carousel-card"),
        Carousel(  # (5)!
            id="carousel",
            items=[
                {"key": "1", "src": "assets/slide_1.jpg"},
                {"key": "2", "src": "assets/slide_2.jpg"},
            ],
            actions=[
                vm.Action(  # (6)!
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
