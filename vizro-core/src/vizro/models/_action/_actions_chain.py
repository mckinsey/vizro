from functools import partial
from typing import Any, Dict, List, NamedTuple

try:
    from pydantic.v1 import validator
except ImportError:  # pragma: no cov
    from pydantic import validator

from vizro.models import Action, VizroBaseModel


class Trigger(NamedTuple):
    component_id: str
    component_property: str


class ActionsChain(VizroBaseModel):
    trigger: Trigger
    actions: List[Action] = []


# Validators for reuse in other models to convert to ActionsChain
def _set_actions(actions: List[Action], values: Dict[str, Any], trigger_property: str) -> List[ActionsChain]:
    return [
        ActionsChain(
            trigger=Trigger(component_id=values["id"], component_property=trigger_property),
            actions=actions,
        )
    ]


def _action_validator_factory(trigger_property: str):
    set_actions = partial(_set_actions, trigger_property=trigger_property)
    return validator("actions", allow_reuse=True)(set_actions)
