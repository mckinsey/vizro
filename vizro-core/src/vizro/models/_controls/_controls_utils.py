from collections.abc import Generator

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


def check_targets_present_on_page(control: ControlType) -> None:
    page = model_manager._get_model_page(control)

    if page is None:
        raise ValueError(f"Control {control.id} should be defined within a Page object.")

    if control not in page.controls:
        page_containers = model_manager._get_models(model_type=Container, root_model=page)
        root_model = next(
            (container for container in page_containers if control in container.controls),
        )

        _validate_targets(control.targets, root_model)

    _validate_targets(control.targets, page)


def set_container_control_default(control: ControlType) -> None:
    page = model_manager._get_model_page(control)
    if control not in page.controls and isinstance(control.selector, (Checklist, RadioItems)):
        control.selector.extra.setdefault("inline", True)
