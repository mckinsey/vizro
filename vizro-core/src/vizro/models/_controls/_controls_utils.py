from __future__ import annotations

import warnings
from collections.abc import Generator, Iterable
from typing import TYPE_CHECKING, Any, cast

from typing_extensions import TypeIs

from vizro.managers import model_manager
from vizro.managers._model_manager import FIGURE_MODELS
from vizro.models import (
    Cascader,
    Checklist,
    Container,
    DatePicker,
    DateTimePicker,
    Dropdown,
    RadioItems,
    RangeSlider,
    Slider,
    Switch,
    TimePicker,
    VizroBaseModel,
)
from vizro.models._components.form._form_utils import get_dict_options_and_value
from vizro.models._components.form.cascader import get_cascader_default_value
from vizro.models.types import ControlType, ModelID, SelectorType

if TYPE_CHECKING:
    from vizro.models import Page

SELECTORS: dict[str, tuple[type, ...]] = {
    "numerical": (RangeSlider, Slider),
    "categorical": (Checklist, Dropdown, RadioItems),
    "date": (DatePicker,),
    "datetime": (DateTimePicker,),
    "time": (TimePicker,),
    "boolean": (Switch,),
    "hierarchical": (Cascader,),
}


# Type-narrowing functions to avoid needing to cast every time we do isinstance for a selector.
def _is_numerical_or_date_selector(x: object) -> TypeIs[RangeSlider | Slider | DatePicker]:
    return isinstance(x, SELECTORS["numerical"] + SELECTORS["date"])


def _is_datetime_selector(x: object) -> TypeIs[DateTimePicker]:
    return isinstance(x, SELECTORS["datetime"])


def _is_categorical_selector(x: object) -> TypeIs[Checklist | Dropdown | RadioItems]:
    return isinstance(x, SELECTORS["categorical"])


def _is_boolean_selector(x: object) -> TypeIs[Switch]:
    return isinstance(x, SELECTORS["boolean"])


def _is_hierarchical_selector(x: object) -> TypeIs[Cascader]:
    return isinstance(x, SELECTORS["hierarchical"])


def _validate_targets(targets: list[str], root_model: VizroBaseModel) -> None:
    component_figures: Generator[VizroBaseModel] = model_manager._get_models(FIGURE_MODELS, root_model)
    component_figure_ids = [model.id for model in component_figures]
    for target in targets:
        if (target_id := target.split(".")[0]) not in component_figure_ids:
            raise ValueError(f"Target {target_id} not found within the {root_model.id}.")


# TODO: Consider rewriting the model_manager._get_model_page to model_manager._get_model_parent()
#  This would make the following renaming logical: model_manager._get_models -> model_manager._get_model_children.
#  These two new methods could have the same signature.
#  Consider adding the parent_model_id to the VizroBaseModel and use that to find the parent model more easily.
def get_control_parent(control: ControlType) -> Page | Container | None:
    """Get the nearest ancestor Container or Page for the given control."""
    # Return None if the control is not part of any page.
    if (page := model_manager._get_model_page(model=control)) is None:
        return None

    nearest_ancestor_container = None
    # Find the deepest Container that contains this control (DFS pre-order in `_get_models` gives deepest match last).
    for container in model_manager._get_models(model_type=Container, root_model=page):
        if control in model_manager._get_models(model_type=type(control), root_model=container):
            nearest_ancestor_container = container

    # Fallback to the page if not nested inside any container.
    return nearest_ancestor_container or page


def extract_control_targets(control: ControlType) -> list[ModelID]:
    """Split control (Filter/Parameter) targets out of ``control.targets``, validating and returning them.

    A Filter/Parameter can target another control to keep the two in sync (see the `set_control` action). Such
    "control targets" are validated and semantically different from "figure targets", so this removes them from
    ``control.targets`` in place and returns them separately. The remaining figure targets are validated later by
    `check_control_targets`.

    A control target must be a *different* control on the *same page*: self-targeting would create a self-referential
    sync loop, and the underlying `set_control` sync runs within a single page.
    """
    from vizro.models._controls import Filter, Parameter

    targeted_controls: list[ModelID] = []
    for target in control.targets.copy():
        if not (target in model_manager and isinstance(model_manager[target], (Filter, Parameter))):
            continue

        # Forbid self-targeting: a control targeting itself would create a self-referential sync loop.
        if target == control.id:
            raise ValueError(f"Control '{control.id}' cannot target itself. Remove '{target}' from its `targets`.")

        # Control targets must be on the same page as the control that targets them.
        if model_manager._get_model_page(control) is not model_manager._get_model_page(model_manager[target]):
            raise ValueError(
                f"Control '{control.id}' cannot target control '{target}' because they are on different pages. "
                f"A control can only target other controls on the same page."
            )

        control.targets.remove(target)
        # Deduplicate so a control listed more than once does not generate duplicate set_control sync actions.
        if target not in targeted_controls:
            targeted_controls.append(target)

    return targeted_controls


def build_control_sync_actions(
    selector: SelectorType, targeted_controls: list[ModelID], update_targets_id: str, update_targets: list[str]
) -> None:
    """Set a control selector's default action chain: sync each targeted control, then refresh its targets.

    Filter and Parameter share this: on selector change they first push the new value to every control they keep in
    sync (via `set_control`), then refresh their own targets (via `update_targets`). The `set_control` actions run
    first so the latest value is applied before the refresh.

    The actions are assigned to ``selector.actions`` first (which wires each action's parent model) and only then
    pre-built, so their `pre_build` validations and internal attributes resolve correctly.
    """
    # Local import to avoid a circular import between this module and vizro.actions.
    from vizro.actions import set_control
    from vizro.actions import update_targets as update_targets_action

    selector.actions = [
        *[set_control(control=control_id, value=None) for control_id in targeted_controls],
        update_targets_action(id=update_targets_id, targets=update_targets),
    ]
    for action in selector.actions:
        action.pre_build()


def check_control_targets(control: ControlType) -> None:
    root_model = get_control_parent(control=control)
    # Search by using "_get_models" instead of "if control not in root_model.controls" to handle nested custom controls.
    if root_model is None or control not in model_manager._get_models(root_model=root_model.controls):
        raise ValueError(f"Control {control.id} should be defined within Page.controls or Container.controls.")

    _validate_targets(targets=control.targets, root_model=root_model)


def warn_missing_id_for_url_control(control: ControlType) -> None:
    if control.show_in_url and "id" not in control.model_fields_set:
        warnings.warn(
            "`show_in_url=True` is set but no `id` was provided. "
            "Shareable URLs might be unreliable if your dashboard configuration changes in future. "
            "If you want to ensure that links continue working, set a fixed `id`.",
            UserWarning,
        )


def get_selector_default_value(selector: SelectorType) -> Any:  # noqa: PLR0911
    """Get default value for a selector if not explicitly provided.

    This is used to set selector.value in controls so that the "Reset controls" button works. Ideally it would be
    done elsewhere, e.g. in the selector models themselves, but that is tricky to get in the right order because it
    would require running the selector.pre_build as part of Filter.pre_build.
    """
    if selector.value is not None:
        return selector.value

    if _is_numerical_or_date_selector(selector):
        is_range = isinstance(selector, RangeSlider) or getattr(selector, "range", False)
        return [selector.min, selector.max] if is_range else selector.min
    elif _is_categorical_selector(selector):
        is_multi = isinstance(selector, Checklist) or getattr(selector, "multi", False)
        _, default_value = get_dict_options_and_value(options=selector.options, value=None, multi=is_multi)
        return default_value
    elif _is_hierarchical_selector(selector):
        is_multi = getattr(selector, "multi", False)
        return get_cascader_default_value(
            selector.options, multi=is_multi, full_path=getattr(selector, "full_path", False)
        )
    elif isinstance(selector, TimePicker):
        # dmc.TimePicker needs "" rather than None to properly set originalValue for resetting control.
        return ["", ""] if selector.range else ""
    elif isinstance(selector, DateTimePicker):
        # Initial value uses date-only ISO strings (no time component) so the inline TimePicker
        # shows as cleared (--:--). The filter logic pads date-only ranges to start-of-day / end-of-day,
        # so the dashboard still shows the full date range by default — exactly matches DatePicker's
        # default behavior with the added "time can be set later" affordance.
        if selector.range:
            datetime_default: Any = (
                [f"{selector.min}", f"{selector.max}"]
                if (selector.min is not None and selector.max is not None)
                else ["", ""]
            )
        else:
            datetime_default = f"{selector.min}" if selector.min is not None else ""
        return datetime_default
    # Boolean selectors always have a default value specified so no need to handle them here.
    return None


def get_selector_parent_control(selector: SelectorType) -> ControlType:
    """Get the parent control of a selector."""
    from vizro.models import Filter, Parameter

    for candidate_parent in cast(
        Iterable[ControlType], [*model_manager._get_models(Parameter), *model_manager._get_models(Filter)]
    ):
        if selector is candidate_parent.selector:
            return candidate_parent

    raise ValueError(f"Selector {selector.id} does not have a parent control.")
