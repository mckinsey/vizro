from functools import partial
from typing import NamedTuple

from pydantic import ValidationInfo

from vizro.managers import model_manager
from vizro.models import VizroBaseModel
from vizro.models.types import ActionType


class Trigger(NamedTuple):
    component_id: str
    component_property: str


class ActionsChain(VizroBaseModel):
    trigger: Trigger
    actions: list[ActionType] = []


# Validators for reuse in other models to convert to ActionsChain
def _set_actions(actions: list[ActionType], info: ValidationInfo, trigger_property: str) -> list[ActionsChain]:
    from vizro.actions import export_data, filter_interaction

    converted_actions = []

    # Convert any built in actions written in the old style vm.Action(function=filter_interaction(...)) or
    # vm.Action(function=export_data(...)) to the new style filter_interaction(...) or export_data(...).
    # We need to delete the old action models from the model manager so they don't get built. After that,
    # built in actions are always handled in the new way.
    for action in actions:
        if isinstance(action.function, (export_data, filter_interaction)):
            del model_manager[action.id]
            converted_actions.append(action.function)
        else:
            converted_actions.append(action)

    return [
        ActionsChain(
            trigger=Trigger(component_id=info.data["id"], component_property=trigger_property),
            actions=converted_actions,
        )
    ]


def _action_validator_factory(trigger_property: str):
    set_actions = partial(_set_actions, trigger_property=trigger_property)
    return set_actions
