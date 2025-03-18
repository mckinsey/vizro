from collections.abc import Generator

from vizro.managers import model_manager
from vizro.managers._model_manager import FIGURE_MODELS
from vizro.models import VizroBaseModel
from vizro.models.types import ControlType


def check_targets_present_on_page(control: ControlType) -> None:
    control_page = model_manager._get_model_page(control)

    if control_page is None:
        raise ValueError(f"Control {control.id} should be defined within a Page object.")

    page_figures: Generator[VizroBaseModel] = model_manager._get_models(FIGURE_MODELS, control_page)
    page_figure_ids = [model.id for model in page_figures]

    for target in control.targets:
        target_id = target.split(".")[0] if "." in target else target
        if target_id not in page_figure_ids:
            raise ValueError(f"Target {target_id} not found within the page {control_page.id}.")
