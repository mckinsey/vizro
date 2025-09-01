from typing import Annotated, Literal

import dash_bootstrap_components as dbc
import vizro.models as vm
from pydantic import model_validator
from vizro import Vizro
from vizro.models._models_utils import make_actions_chain
from vizro.models.types import ActionsType, capture


class Carousel(vm.VizroBaseModel):
    type: Literal["carousel"] = "carousel"
    images: list[str]
    # actions: ActionsType = []
    #
    # @model_validator(mode="after")
    # def _make_actions_chain(self):
    #     return make_actions_chain(self)

    #         @property
    # def _action_triggers(self):
    #     return {"__default__": f"{self.id}.active_index"}

    # @property
    # def _action_inputs(self):
    #     return {"__default__": f"{self.id}.active_index"}
    #
    # @property
    # def _action_triggers(self):
    #     return {"__default__": f"{self.id}.active_index"}
    #
    # @property
    # def _action_outputs(self):
    #     return {"__default__": f"{self.id}.active_index"}

    def build(self):
        return dbc.Carousel(id=self.id, items=[{"src": item} for item in self.images])


vm.Page.add_type("components", Carousel)


@capture("action")
def slide_next_card(active_index):
    if active_index:
        return "Second slide"
    return "First slide"


@capture("action")
def go_to_slide_3():
    return 1


page = vm.Page(
    title="Custom Component",
    # layout=vm.Flex(),
    # layout=vm.Grid(grid=[[0, 1], [2, -1]]),
    components=[
        Carousel(
            id="carousel",
            images=[
                "assets/slide_1.png",
                "assets/slide_2.png",
                "assets/slide_3.png",
            ],
            # actions=[
            #     vm.Action(
            #         function=slide_next_card("carousel"),
            #         outputs="carousel-card",
            #     )
            # ],
        ),
        vm.Card(text="First slide", id="carousel-card"),
        vm.Button(text="Go to slide 2"),  # , actions=vm.Action(function=go_to_slide_3(), outputs="carousel")),
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run(debug=True)
