from functools import partial
from typing import NamedTuple

from pydantic import ValidationInfo

from vizro.models import Action, VizroBaseModel


class Trigger(NamedTuple):
    component_id: str
    component_property: str


class ActionsChain(VizroBaseModel):
    trigger: Trigger
    actions: list[Action] = []


# Validators for reuse in other models to convert to ActionsChain
def _set_actions(value: list[Action], info: ValidationInfo, trigger_property: str) -> list[ActionsChain]:
    return [
        ActionsChain(
            trigger=Trigger(component_id=info.data["id"], component_property=trigger_property),
            actions=value,
        )
    ]


def _action_validator_factory(trigger_property: str):
    set_actions = partial(_set_actions, trigger_property=trigger_property)
    return set_actions
