from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Literal
from pydantic import model_validator

import vizro.models as vm
from vizro import Vizro
from vizro.models._models_utils import make_actions_chain
from vizro.models.types import capture, ActionsType
import dash_mantine_components as dmc


class Rating(vm.VizroBaseModel):
    type: Literal["rating"] = "rating"
    actions: ActionsType

    _make_actions_chain = model_validator(mode="after")(make_actions_chain)

    @property
    def _action_triggers(self):
        return {"__default__": f"{self.id}.value"}

    @property
    def _action_inputs(self):
        return {"__default__": f"{self.id}.value"}

    @property
    def _action_outputs(self):
        return {"__default__": f"{self.id}.value"}

    def build(self):
        rating = dmc.Rating(id="rating")

        return rating


@capture("action")
def clear_rating():
    return 0


@capture("action")
def update_rating(value):
    if value:
        return f"You gave a rating of {value} out of 5 stars"
    return "You have not provided a rating"


vm.Page.add_type("components", Rating)

page = vm.Page(
    title="Custom component",
    layout=vm.Flex(direction="row"),
    components=[
        Rating(id="rating", actions=vm.Action(function=update_rating("rating"), outputs="rating_text")),
        vm.Button(text="Clear rating", actions=vm.Action(function=clear_rating(), outputs="rating")),
        vm.Text(id="rating_text", text="You have not provided a rating"),
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
