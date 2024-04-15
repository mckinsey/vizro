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
# TODO-AV2: Rethink 'component_id_prefix' and 'actions_chain_id'
def _set_actions(
    actions: List[Action],
    values: Dict[str, Any],
    trigger_property: str,
    component_id_prefix: str = "",
    actions_chain_id: str = None,
) -> List[ActionsChain]:
    actions_chain = [
        ActionsChain(
            trigger=Trigger(component_id=f'{component_id_prefix}{values["id"]}', component_property=trigger_property),
            actions=actions,
        )
    ]
    if actions_chain_id:
        actions_chain[0].id = f'{actions_chain_id}{values["id"]}'

    return actions_chain


def _action_validator_factory(trigger_property: str, component_id_prefix: str = "", actions_chain_id: str = None):
    set_actions = partial(
        _set_actions,
        trigger_property=trigger_property,
        component_id_prefix=component_id_prefix,
        actions_chain_id=actions_chain_id,
    )
    return validator("actions", allow_reuse=True)(set_actions)
