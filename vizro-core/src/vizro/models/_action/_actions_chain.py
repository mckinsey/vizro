from typing import NamedTuple

from vizro.models import VizroBaseModel
from vizro.models.types import ActionType


class Trigger(NamedTuple):
    component_id: str
    component_property: str


class ActionsChain(VizroBaseModel):
    trigger: Trigger
    actions: list[ActionType] = []
