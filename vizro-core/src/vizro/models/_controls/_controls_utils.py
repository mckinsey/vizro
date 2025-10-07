import warnings
from collections.abc import Generator
from typing import Optional

from vizro.managers import model_manager
from vizro.managers._model_manager import FIGURE_MODELS
from vizro.models import Checklist, Container, DatePicker, Dropdown, RadioItems, RangeSlider, Slider, VizroBaseModel
from vizro.models._components.form._form_utils import get_dict_options_and_default
from vizro.models.types import ControlType, SelectorType


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


def warn_missing_id_for_url_control(control: ControlType) -> None:
    if control.show_in_url and "id" not in control.model_fields_set:
        warnings.warn(
            "`show_in_url=True` is set but no `id` was provided. "
            "Shareable URLs might be unreliable if your dashboard configuration changes in future. "
            "If you want to ensure that links continue working, set a fixed `id`.",
            UserWarning,
        )


def set_selector_default_value(control_selector: SelectorType) -> None:
    """Set default value for the control's selector if not explicitly provided."""
    if control_selector.value is not None:
        return

    if isinstance(control_selector, (Slider, RangeSlider, DatePicker)):
        is_range = isinstance(control_selector, RangeSlider) or getattr(control_selector, "range", False)
        control_selector.value = [control_selector.min, control_selector.max] if is_range else control_selector.min
    elif isinstance(control_selector, (Checklist, Dropdown, RadioItems)):
        is_multi = isinstance(control_selector, Checklist) or getattr(control_selector, "multi", False)
        _, default_value = get_dict_options_and_default(options=control_selector.options, multi=is_multi)
        control_selector.value = default_value
