import warnings
from collections.abc import Generator
from typing import Any, Optional, Union

from typing_extensions import TypeIs

from vizro.managers import model_manager
from vizro.managers._model_manager import FIGURE_MODELS
from vizro.models import (
    Checklist,
    Container,
    DatePicker,
    Dropdown,
    RadioItems,
    RangeSlider,
    Slider,
    Switch,
    VizroBaseModel,
)
from vizro.models._components.form._form_utils import get_dict_options_and_default
from vizro.models.types import ControlType, SelectorType

SELECTORS: dict[str, tuple[type, ...]] = {
    "numerical": (RangeSlider, Slider),
    "categorical": (Checklist, Dropdown, RadioItems),
    "temporal": (DatePicker,),
    "boolean": (Switch,),
}


# Type-narrowing functions to avoid needing to cast every time we do isinstance for a selector.
def _is_numerical_temporal_selector(x: object) -> TypeIs[Union[RangeSlider, Slider, DatePicker]]:
    return isinstance(x, SELECTORS["numerical"] + SELECTORS["temporal"])


def _is_categorical_selector(x: object) -> TypeIs[Union[Checklist, Dropdown, RadioItems]]:
    return isinstance(x, SELECTORS["categorical"])


def _is_boolean_selector(x: object) -> TypeIs[Switch]:
    return isinstance(x, SELECTORS["boolean"])


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


def get_selector_default_value(selector: SelectorType) -> Any:
    """Get default value for a selector if not explicitly provided.

    This is used to set selector.value in controls so that the "Reset controls" button works. Ideally it would be
    done elsewhere, e.g. in the selector models themselves, but that is tricky to get in the right order because it
    would require running the selector.pre_build as part of Filter.pre_build.
    """
    if selector.value is not None:
        return selector.value

    if _is_numerical_temporal_selector(selector):
        is_range = isinstance(selector, RangeSlider) or getattr(selector, "range", False)
        return [selector.min, selector.max] if is_range else selector.min
    elif _is_categorical_selector(selector):
        is_multi = isinstance(selector, Checklist) or getattr(selector, "multi", False)
        _, default_value = get_dict_options_and_default(options=selector.options, multi=is_multi)
        return default_value
    # Boolean selectors always have a default value specified so no need to handle them here.
