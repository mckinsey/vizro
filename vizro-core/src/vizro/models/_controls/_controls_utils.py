from collections.abc import Generator
from typing import Optional

from vizro.managers import model_manager
from vizro.managers._model_manager import FIGURE_MODELS
from vizro.models import Checklist, Container, RadioItems, VizroBaseModel
from vizro.models.types import ControlType


def _validate_targets(targets: list[str], root_model: VizroBaseModel) -> None:
    component_figures: Generator[VizroBaseModel] = model_manager._get_models(FIGURE_MODELS, root_model)
    component_figure_ids = [model.id for model in component_figures]
    for target in targets:
        target_id = target.split(".")[0]
        if target_id not in component_figure_ids:
            raise ValueError(f"Target {target_id} not found within the {root_model.id}.")


# TODO: Consider rewriting the model_manager._get_model_page to model_manager._get_model_parent()
#  This would make the following renaming logical: model_manager._get_models -> model_manager._get_model_children.
#  These two new methods could have the same signature.
#  Consider adding the parent_model_id to the VizroBaseModel and use that to find the parent model more easily.
def _get_control_parent(control: ControlType) -> Optional[VizroBaseModel]:
    """Get the parent model of a control."""
    # Return None if the control is not part of any page.
    if (page := model_manager._get_model_page(model=control)) is None:
        return None

    # Return the Page if the control is its direct child.
    if control in page.controls:
        return page

    # Otherwise, return the Container that contains the control.
    page_containers = model_manager._get_models(model_type=Container, root_model=page)
    return next(container for container in page_containers if control in container.controls)


def check_control_targets(control: ControlType) -> None:
    if (root_model := _get_control_parent(control=control)) is None:
        raise ValueError(f"Control {control.id} should be defined within a Page object.")

    _validate_targets(targets=control.targets, root_model=root_model)


def set_container_control_default(control: ControlType) -> None:
    page = model_manager._get_model_page(control)
    if control not in page.controls and isinstance(control.selector, (Checklist, RadioItems)):
        control.selector.extra.setdefault("inline", True)
